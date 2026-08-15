"""fusion.dual_memory — couplage bidirectionnel LLM (mémoire textuelle) × RATIS (mémoire logique).

THESE (Jonathan Evina) : il existe deux mémoires fondamentales
  - Mémoire TEXTUELLE : retient le mot, la séquence, la distribution. C'est ce
    que fait un LLM statistique (Qwen, Needle). Il mémorise la forme de surface
    mais sans le sens logique de représentation.
  - Mémoire LOGIQUE : retient la logique de représentation du mot, sa cohérence,
    son ancrage environnemental (ETH), sa persistance topologique (P_sig). C'est
    ce que fait RATIS-Net. Il ne retient pas « bonjour », il retient sa FORME
    topologique et son sens dans le milieu.

Les deux couplées se comportent comme les mémoires du cerveau (déclarative +
procédurale/émotionnelle). On ne peut pas vraiment les séparer : un LLM seul
est un perroquet statistique (hallucine) ; RATIS seul est une forme sans voix.
Le couplage EST la cognition.

BOUCLE DE CONVERGENCE :
  1. LLM génère une réponse (mémoire textuelle).
  2. RATIS évalue la réponse (mémoire logique) : P_sig, émotion, cohérence.
  3. Si la réponse converge (P_sig haut + émotion cohérente avec l'entrée) → CERTIFIÉ.
  4. Sinon, RATIS renvoie son signal (l'émotion perçue + le manque de cohérence)
     comme FEEDBACK → le LLM régénère, ancré par le signal logique.
  5. Itérer jusqu'à convergence ou épuisement des tours.

La loi LCT est FIGÉE. Ce module ne modifie pas la loi, il l'utilise comme
guide du couplage.
"""
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import requests

_FUSION_ROOT = Path(__file__).resolve().parent
if str(_FUSION_ROOT) not in sys.path:
    sys.path.insert(0, str(_FUSION_ROOT))

from fusion.bridge import (  # noqa: E402
    RatisFusionAgent, _message_coherence, env_from_name,
)


@dataclass
class ConvergenceTurn:
    """Un tour de la boucle de convergence."""
    turn: int
    llm_response: str            # ce que le LLM a dit (mémoire textuelle)
    p_sig: float                 # cohérence topo (mémoire logique)
    emotion: str                 # émotion perçue par RATIS
    coherence: float             # cohérence LCT
    converged: bool              # la réponse a-t-elle convergé ?
    feedback: str                # signal logique renvoyé au LLM


@dataclass
class ConvergenceResult:
    """Résultat de la boucle de convergence bidirectionnelle."""
    message: str
    env_name: str
    turns: list = field(default_factory=list)
    final_response: str = ""
    final_certified: bool = False
    final_p_sig: float = 0.0
    final_emotion: str = ""
    n_turns: int = 0
    converged: bool = False
    latency_ms: float = 0.0
    llm_alone_response: str = ""   # réponse du LLM seul (sans couplage) pour comparaison

    def to_dict(self) -> dict:
        return asdict(self)


class DualMemoryCoupler:
    """Couple un LLM (mémoire textuelle) avec RATIS (mémoire logique).

    Le couplage est BIDIRECTIONNEL :
      - RATIS filtre la sortie du LLM (mémoire logique évalue mémoire textuelle)
      - RATIS renvoie un signal logique qui guide la régénération du LLM
        (mémoire logique nourrit mémoire textuelle)
    """

    def __init__(self, agent: RatisFusionAgent, ollama_url: str = "http://127.0.0.1:11434",
                 model: str = "qwen2.5:0.5b", max_turns: int = 4,
                 p_sig_convergence: float = 0.5, emotion_match_threshold: float = 0.5):
        self.agent = agent
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.max_turns = max_turns
        self.p_sig_convergence = p_sig_convergence
        self.emotion_match_threshold = emotion_match_threshold

    def _llm_generate(self, prompt: str, system: str = "") -> str:
        """Génère du texte avec le LLM (mémoire textuelle)."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 80},
        }
        if system:
            payload["system"] = system
        try:
            r = requests.post(f"{self.ollama_url}/api/generate",
                              json=payload, timeout=60)
            r.raise_for_status()
            return r.json().get("response", "").strip()
        except Exception as e:
            return f"(erreur LLM: {e})"

    def _emotion_to_phrase(self, emotion: str, env_name: str) -> str:
        """Traduit l'émotion RATIS en une phrase de guidage pour le LLM."""
        phrases = {
            "joie": "respond warmly and positively, you feel joy",
            "colère": "respond with firm concern, you feel tension",
            "tristesse": "respond with gentle empathy, you feel sadness",
            "neutre": "respond calmly and clearly",
        }
        return phrases.get(emotion, "respond clearly") + f" (environment: {env_name})"

    def _build_guided_prompt(self, message: str, env_name: str,
                             emotion: str, p_sig: float, turn: int) -> str:
        """Construit un prompt ancré par le signal logique de RATIS."""
        emo_phrase = self._emotion_to_phrase(emotion, env_name)
        if turn == 0:
            return (f"You are RATIS, a sovereign agent. {emo_phrase}. "
                    f"Reply in ONE short sentence to: {message}")
        return (f"You are RATIS. {emo_phrase}. "
                f"Your previous reply lacked topological coherence (P_sig={p_sig:.2f}, "
                f"too low). Reply again in ONE short, coherent sentence to: {message}")

    def converge(self, message: str, env_name: str = "neutre") -> ConvergenceResult:
        """Boucle de convergence LLM ↔ RATIS jusqu'à certification."""
        t0 = time.time()
        env = env_from_name(env_name)
        result = ConvergenceResult(message=message, env_name=env_name)

        # ── Référence : LLM seul (mémoire textuelle pure, sans couplage) ──
        result.llm_alone_response = self._llm_generate(
            f"Reply in ONE short sentence to: {message}")

        # ── Boucle de convergence (couplage bidirectionnel) ──
        emotion = "neutre"
        for turn in range(self.max_turns):
            # 1. RATIS perçoit l'émotion de l'entrée (mémoire logique)
            ratis_thought = self.agent.ratis.think(message, env)
            emotion = ratis_thought.emotion_understood
            p_sig_input = _message_coherence(message)

            # 2. LLM génère ancré par le signal logique (mémoire textuelle guidée)
            prompt = self._build_guided_prompt(message, env_name, emotion, p_sig_input, turn)
            llm_response = self._llm_generate(prompt)

            # 3. RATIS évalue la sortie du LLM (mémoire logique évalue mémoire textuelle)
            p_sig_out = _message_coherence(llm_response)
            out_thought = self.agent.ratis.think(llm_response, env)
            emotion_out = out_thought.emotion_understood

            # 4. Test de convergence
            emotion_match = (emotion == emotion_out) or (
                abs(ratis_thought.c_seuil - out_thought.c_seuil) < self.emotion_match_threshold)
            converged = p_sig_out >= self.p_sig_convergence and emotion_match

            feedback = (f"P_sig={p_sig_out:.2f} "
                        f"(≥{self.p_sig_convergence:.2f}), "
                        f"emotion in={emotion} vs out={emotion_out} "
                        f"({'match ✓' if emotion_match else 'mismatch ✗'})")

            result.turns.append(ConvergenceTurn(
                turn=turn, llm_response=llm_response,
                p_sig=round(p_sig_out, 4), emotion=emotion_out,
                coherence=round(out_thought.confidence, 4),
                converged=converged, feedback=feedback,
            ))

            if converged:
                break

        # ── Finalisation ──
        final = result.turns[-1] if result.turns else None
        if final:
            result.final_response = final.llm_response
            result.final_p_sig = final.p_sig
            result.final_emotion = final.emotion
            result.final_certified = final.converged
            result.converged = final.converged
            result.n_turns = len(result.turns)

        result.latency_ms = round((time.time() - t0) * 1000, 1)
        return result


def build_coupler(tools=None, **kwargs) -> DualMemoryCoupler:
    """Construit un coupleur LLM↔RATIS prêt à l'emploi."""
    agent = RatisFusionAgent(tools=tools, **kwargs)
    return DualMemoryCoupler(agent)
