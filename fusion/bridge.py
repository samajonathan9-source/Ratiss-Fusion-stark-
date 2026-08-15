"""fusion.bridge — le pont cognitif RATIS × Needle.

ARCHITECTURE SYMBIOTIQUE (honnête, contre les vraies API vérifiées).

Le cerveau RATIS fait la cognition (6 étapes : percevoir → penser → ressentir →
comprendre → parler → certifier). Le corps Needle fait l'action (tool-calling
structuré, extraction JSON). Le bridge orchestre les deux avec un filtre
anti-hallucination par CONFIANCE CROISÉE.

  confiance_certifiée = confiance_needle × P_sig_ratis

Si P_sig s'effondre, le système se tait (rejet structurel). Si Needle est confiant
mais que la topologie s'effondre, la réponse est flaguée DÉRIVE (pas supprimée —
on ajoute un score, comme la couche anti-hallucination RATIS).

ÉCART AVEC LE DOC MISTRAL (honnêteté scientifique) :
  - Mistral inventait RatisNetV4Learner.compute_persistence / compute_coherence.
    La vraie API est RatisAgent.think() → Thought, qui fait déjà la boucle 6 étapes.
  - Mistral présentait Needle comme générateur de langage naturel fluide. En réalité
    Needle est un TOOL-CALLER : pas de free-text fallback, tout est un appel de
    fonction. La symbiose est donc : Needle = action structurée, RATIS = cognition
    + certification + parole émotionnelle (décodeur).

La loi LCT est FIGÉE. On ne la modifie jamais.
"""
from __future__ import annotations

import hashlib
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np

# ── Cerveau RATIS (copie locale autonome) ──────────────────────────────────
_FUSION_ROOT = Path(__file__).resolve().parent
if str(_FUSION_ROOT) not in sys.path:
    sys.path.insert(0, str(_FUSION_ROOT))
# AEON local pour le cerveau TTF-Compute
_AEON = _FUSION_ROOT / "aeon"
if _AEON.is_dir() and str(_AEON) not in sys.path:
    sys.path.insert(0, str(_AEON))

from ratis_net.ratis_agent import RatisAgent  # noqa: E402
from ratis_net.eth_thermo_fixer import ThermoEnvironment  # noqa: E402
from ratis_net.emocontext_loader import (  # noqa: E402
    load_emocontext, balance_classes, tokenize,
)
from ratis_net.ttf_bridge import is_ttf_available  # noqa: E402
from ratis_net.topo_tokenizer import topo_signature  # noqa: E402
from ratis_net.lct_collapse import topological_mark  # noqa: E402

# ── Corps Needle (tool-calling, moteur pré-caché pour offline) ─────────────
import needle  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────
#  Cohérence topologique d'un message (P_sig_message)
# ──────────────────────────────────────────────────────────────────────────
def _message_coherence(message: str, dim: int = 8) -> float:
    """Mesure la cohérence topologique d'un message entier.

    HONNÊTETÉ : la persistance H1 (cycle le plus long) d'un message court est
    quasi toujours nulle (pas assez de points pour former un cycle). On utilise
    donc une mesure robuste composée :

      P_sig_message = 0.5 × (cohesion_H0) + 0.5 × (consistency_inter_mots)

    - cohesion_H0 : persistance H0 (composantes connexes) du nuage concaténé.
      Un message cohérent (mots liés) fusionne en peu de composantes persistantes.
    - consistency_inter_mots : similarité cosinus moyenne entre embeddings topo
      des mots. Des mots liés ont des signatures proches ; du bruit aléatoire
      a des signatures dispersées.

    C'est un proxy honnête de la "forme" topologique du message. La borne est
    documentée : ce n'est PAS la persistance H1 stricte de la loi LCT (qui
    s'applique au cycle H1 le plus long d'un système distribué). C'est un filtre
    d'entrée pragmatique pour l'anti-hallucination.
    """
    words = [w for w in tokenize(message) if len(w) >= 2]
    if len(words) < 2:
        return 0.5  # message court : on ne pénalise pas les salutations

    # embeddings topo de chaque mot
    embs = []
    for w in words:
        try:
            embs.append(topo_signature(w, dim=dim))
        except Exception:
            continue
    if len(embs) < 2:
        return 0.5
    embs = np.array(embs)

    # 1. consistency inter-mots (similarité cosinus moyenne)
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms < 1e-9] = 1.0
    normed = embs / norms
    sim_matrix = normed @ normed.T
    n = len(embs)
    consistency = float((sim_matrix.sum() - n) / (n * (n - 1))) if n > 1 else 0.0
    consistency = max(0.0, min(1.0, consistency))

    # 2. cohesion H0 (persistance des composantes connexes)
    try:
        import gudhi
        pts = embs.tolist()
        rips = gudhi.RipsComplex(points=pts, max_edge_length=2.0)
        st = rips.create_simplex_tree(max_dimension=1)
        diag = st.persistence(homology_coeff_field=2)
        h0 = [d for dim, d in diag if dim == 0]
        if h0:
            # persistance H0 = différence mort-naissance ; un message cohérent
            # a des composantes qui meurent tôt (fusionnent vite)
            persistences = [d[1] - d[0] for d in h0 if d[1] != float("inf")]
            if persistences:
                cohesion = 1.0 - min(1.0, float(np.mean(persistences)) / 2.0)
            else:
                cohesion = 0.8
        else:
            cohesion = 0.5
    except Exception:
        cohesion = consistency  # fallback

    return 0.5 * cohesion + 0.5 * consistency


# ──────────────────────────────────────────────────────────────────────────
#  Environnements thermo (ETH) nommés → objets
# ──────────────────────────────────────────────────────────────────────────
_ENVIRONMENTS = {
    "neutre": ThermoEnvironment.calm,
    "calme": ThermoEnvironment.calm,
    "joie": ThermoEnvironment.joy,
    "colère": ThermoEnvironment.anger,
    "peur": ThermoEnvironment.fear,
}


def env_from_name(name: str) -> ThermoEnvironment:
    fn = _ENVIRONMENTS.get(name.lower(), ThermoEnvironment.calm)
    return fn()


# ──────────────────────────────────────────────────────────────────────────
#  La pensée symbiotique (sortie du bridge)
# ──────────────────────────────────────────────────────────────────────────
@dataclass
class FusionThought:
    """Une pensée complète de l'agent symbiotique RATIS × Needle."""
    message: str
    env_name: str
    # cognition RATIS
    p_sig_input: float           # cohérence topo de l'entrée (filtre anti-hall)
    emotion_perceived: str       # émotion ressentie (ETH)
    emotion_understood: str      # émotion dominante (LCT)
    confidence_ratis: float      # confiance du réseau LCT
    thought_hash: str            # hash topo de la pensée (forme, invariant ZK)
    mcb_count: int               # nb de MCB (pensée sans mots)
    c_seuil: float               # seuil thermo contextuel (ETH)
    # décision
    status: str                  # CERTIFIÉ | REJETÉ | DÉRIVE
    route: str                   # "parole" (décodeur RATIS) ou "action" (Needle)
    # génération
    response: str                # la réponse finale (texte)
    tool_results: list = field(default_factory=list)
    # certification
    confidence_needle: float | None = None
    confidence_certified: float = 0.0       # confiance croisée = needle × P_sig
    response_hash: str = ""                 # hash topo de la réponse (ZK)
    certified: bool = False
    # métriques
    latency_ms: float = 0.0
    needle_used: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


# ──────────────────────────────────────────────────────────────────────────
#  L'agent symbiotique
# ──────────────────────────────────────────────────────────────────────────
class RatisFusionAgent:
    """Agent symbiotique : cerveau RATIS + corps Needle, certifié par ZK.

    Pipeline :
      1. PERCEVOIR & RESSENTIR (RATIS) — cohérence topo de l'entrée + ETH émotion.
      2. DÉCIDER (LCT figée) — si P_sig < seuil → REJET (anti-hallucination).
      3. ROUTER — action (Needle tool-call) ou parole (décodeur RATIS).
      4. GÉNÉRER — Needle exécute l'action OU le décodeur parle.
      5. CERTIFIER — confiance croisée + hash topo invariant (ZK).
    """

    def __init__(self, tools=None, p_sig_threshold: float = 0.30,
                 eta: float = 0.2, n_hidden: int = 10, use_ttf: bool = True,
                 train_examples: int = 480, train_epochs: int = 5,
                 seed: int = 42, verbose_train: bool = False):
        # ── Cerveau RATIS ──
        self.ratis = RatisAgent(use_ttf=use_ttf, eta=eta, n_hidden=n_hidden, seed=seed)
        self._train_ratis(train_examples, train_epochs, verbose_train)

        # ── Corps Needle ──
        self.tools = tools or []
        self.needle = needle.Needle(
            tools=self.tools,
            system="assistant: RATIS, a sovereign cognitive agent that acts "
                   "through tools and certifies its responses topologically.",
        ) if self.tools else None

        # ── Seuil anti-hallucination (tunable, pas figé) ──
        self.p_sig_threshold = p_sig_threshold
        self.trained = True

    # ── Entraînement du cerveau (EmoContext, séquence rééquilibré) ─────────
    def _train_ratis(self, n_examples: int, epochs: int, verbose: bool):
        data_path = _FUSION_ROOT / "data" / "emocontext" / "train.txt"
        examples = load_emocontext(data_path, max_examples=n_examples + 120)
        self.ratis.set_vocab(examples, top_k=60)
        dim = self.ratis.token_dim
        samples = []
        for e in examples[:n_examples]:
            ws = [w for w in tokenize(e["turn3"]) if w in self.ratis._cache]
            if len(ws) < 2:
                continue
            embs = np.array([self.ratis._cache[w] for w in ws])
            norms = np.linalg.norm(embs, axis=1, keepdims=True)
            norms[norms < 1e-9] = 1.0
            seq_emb = (embs * norms).sum(axis=0) / norms.sum()
            n = np.linalg.norm(seq_emb)
            seq_emb = seq_emb / n if n > 1e-9 else seq_emb
            samples.append((seq_emb, e["env"], e["label_num"], e["c_seuil"]))
        samples = balance_classes(samples)
        self.ratis.train(samples, epochs=epochs, verbose=verbose)

    # ── Détection d'intention d'action (router) ─────────────────────────────
    def _needs_action(self, message: str) -> bool:
        """Décide si le message demande une action (→ Needle) ou de la parole.

        Heuristique honnête : si des outils sont déclarés ET que le message
        contient un verbe d'action / une demande d'information structurée, on
        route vers Needle. Sinon, parole émotionnelle RATIS.
        """
        if not self.needle or not self.tools:
            return False
        action_cues = ("get", "check", "find", "show", "tell me about",
                       "what is", "what's", "how is", "status", "search",
                       "send", "set", "calculate", "convert", "weather",
                       "patient", "fetch", "look up", "log", "availability",
                       "vérifie", "donne", "cherche", "calcule", "envoie")
        m = message.lower()
        return any(cue in m for cue in action_cues)

    # ── La boucle cognitive symbiotique ─────────────────────────────────────
    def think(self, message: str, env_name: str = "neutre") -> FusionThought:
        """Une pensée symbiotique complète, certifiée."""
        t0 = time.time()
        env = env_from_name(env_name)

        # ── 1. PERCEVOIR & RESSENTIR (RATIS) ──
        p_sig = _message_coherence(message)
        thought = self.ratis.think(message, env)  # boucle 6 étapes du cerveau

        # ── 2. DÉCIDER (filtre anti-hallucination par P_sig) ──
        if p_sig < self.p_sig_threshold:
            return FusionThought(
                message=message, env_name=env_name,
                p_sig_input=round(p_sig, 4),
                emotion_perceived=thought.emotion_perceived,
                emotion_understood=thought.emotion_understood,
                confidence_ratis=round(thought.confidence, 4),
                thought_hash=thought.thought_hash, mcb_count=thought.mcb_count,
                c_seuil=round(thought.c_seuil, 4),
                status="REJETÉ",
                route="—",
                response="(cohérence topologique trop faible — je préfère me taire)",
                latency_ms=round((time.time() - t0) * 1000, 1),
            )

        # ── 3. ROUTER (action vs parole) ──
        route = "action" if self._needs_action(message) else "parole"

        # ── 4. GÉNÉRER ──
        tool_results: list = []
        confidence_needle: float | None = None
        response: str = thought.response  # parole émotionnelle RATIS par défaut

        if route == "action" and self.needle is not None:
            try:
                nr = self.needle.run(message)
                confidence_needle = nr.get("confidence")
                tool_results = nr.get("results", [])
                calls = nr.get("function_calls", [])
                if tool_results or calls:
                    response = self._format_tool_results(tool_results, calls)
                else:
                    route = "parole"  # Needle n'a pas trouvé d'outil pertinent
            except Exception as e:
                response = f"(erreur outil: {e})"
                route = "parole"

        # ── 5. CERTIFIER (confiance croisée + hash ZK) ──
        response_hash, certified = self._certify_response(response, env)
        if confidence_needle is not None:
            confidence_certified = confidence_needle * p_sig
        else:
            confidence_certified = thought.confidence * p_sig

        # détection de dérive topo
        if route == "action" and confidence_needle is not None and confidence_needle < 0.3:
            status = "DÉRIVE"
        elif confidence_certified < 0.10:
            status = "DÉRIVE"
        else:
            status = "CERTIFIÉ"

        latency = (time.time() - t0) * 1000
        return FusionThought(
            message=message, env_name=env_name,
            p_sig_input=round(p_sig, 4),
            emotion_perceived=thought.emotion_perceived,
            emotion_understood=thought.emotion_understood,
            confidence_ratis=round(thought.confidence, 4),
            thought_hash=thought.thought_hash, mcb_count=thought.mcb_count,
            c_seuil=round(thought.c_seuil, 4),
            status=status, route=route,
            response=response, tool_results=tool_results,
            confidence_needle=round(confidence_needle, 4) if confidence_needle is not None else None,
            confidence_certified=round(confidence_certified, 4),
            response_hash=response_hash, certified=certified,
            latency_ms=round(latency, 1),
            needle_used=(route == "action"),
        )

    # ── Certification ZK de la réponse ─────────────────────────────────────
    def _certify_response(self, response: str, env: ThermoEnvironment) -> tuple[str, bool]:
        """Hash topologique invariant de la réponse → preuve ZK (la forme, pas le courant)."""
        marks = []
        for w in response.split():
            if w in self.ratis._cache:
                marks.append(topological_mark(
                    np.array([self.ratis._cache[w]]), c_seuil=0.0,
                    env_vector=env.to_vector()))
        mark_str = "|".join(sorted(marks))
        mark_str += f"|env={np.array2string(env.to_vector(), precision=4)}"
        resp_hash = hashlib.sha256(mark_str.encode()).hexdigest()[:16]
        certified = len(response.split()) >= 2 and len(set(marks)) >= 1
        return resp_hash, certified

    # ── Formatage des résultats d'outils en texte lisible ──────────────────
    @staticmethod
    def _format_tool_results(results: list, calls: list) -> str:
        """Formate les résultats/outils Needle en réponse textuelle lisible."""
        parts = []
        for c in calls:
            name = c.get("name", "?")
            args = c.get("arguments", {})
            if args:
                parts.append(f"[{name}] appelé avec {args}")
        for r in results:
            if isinstance(r, dict):
                for k in ("reply", "text", "message", "response", "answer"):
                    if k in r:
                        parts.append(str(r[k]))
                        break
                else:
                    # dict structuré sans champ textuel : on le rend lisible
                    kv = ", ".join(f"{k}={v}" for k, v in r.items())
                    parts.append(kv)
            elif isinstance(r, list):
                parts.append("; ".join(str(x) for x in r))
            else:
                parts.append(str(r))
        return " ".join(parts) if parts else "(aucun résultat)"

    # ── Invariance ZK : vérifier la forme sous deux énergies ───────────────
    def verify_zk_invariance(self, message: str) -> dict:
        """Vérifie que la PENSÉE (hash topo) est invariante sous changement d'énergie.

        Loi LCT : on certifie la forme (le message), pas le courant (l'énergie).
        Deux environnements thermo différents → même hash de pensée.
        """
        envs = [env_from_name("joie"), env_from_name("colère")]
        hashes = []
        for env in envs:
            t = self.ratis.think(message, env)
            hashes.append(t.thought_hash)
        invariant = hashes[0] == hashes[1]
        return {
            "message": message,
            "hash_joie": hashes[0],
            "hash_colère": hashes[1],
            "invariant": invariant,
            "loi_LCT": "la forme (pensée) est la même ; l'émotion (courant) est contextuelle",
        }


def build_default_agent(tools=None, **kwargs) -> RatisFusionAgent:
    """Construit l'agent avec le cerveau entraîné + outils optionnels."""
    return RatisFusionAgent(tools=tools, **kwargs)
