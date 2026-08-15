"""scripts.demo_fusion — démonstration de l'agent symbiotique RATIS × Needle.

Montre le pipeline complet sur des cas conversationnels et d'action,
avec certification ZK et confiance croisée. Sauvegarde les preuves.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from fusion.bridge import RatisFusionAgent, env_from_name
from fusion.tts import OfflineTTS
from tools.clinical_tools import DEFAULT_TOOLS


def main():
    print("=" * 72)
    print("DÉMO — Agent symbiotique RATIS × Needle")
    print("Cerveau topologique + système nerveux d'exécution, certifié ZK")
    print("=" * 72)

    print("\nInitialisation (entraînement EmoContext + Needle)...")
    t0 = time.time()
    agent = RatisFusionAgent(tools=DEFAULT_TOOLS, train_examples=480, train_epochs=5)
    print(f"Agent prêt en {time.time()-t0:.1f}s")
    print(f"  TTF-Compute (penser) : {agent.ratis.ttf_available}")
    print(f"  Outils Needle (corps): {len(agent.tools)}")

    tts = OfflineTTS()
    print(f"  TTS : {tts.engine_name()}")

    # ── Cas de démonstration ────────────────────────────────────────────────
    cases = [
        # Conversationnel (route parole)
        ("you are amazing and funny", "joie", "parole émotionnelle"),
        ("i feel so lonely and lost", "peur", "parole émotionnelle"),
        ("hello how are you today", "calme", "parole émotionnelle"),
        # Action (route action → Needle)
        ("check the status of patient 123", "calme", "tool-calling clinique"),
        ("check the status of patient 456", "neutre", "tool-calling clinique"),
        ("check the availability of therapy room", "neutre", "tool-calling ressource"),
        # Anti-hallucination
        ("asdfghjkl qqqq zzzz random", "neutre", "test anti-hallucination"),
    ]

    results = []
    print("\n" + "=" * 72)
    print("Boucles cognitives :")
    print("=" * 72)
    for msg, env, desc in cases:
        t = agent.think(msg, env)
        results.append(t.to_dict())
        print(f"\n┌─ [{env}] {msg}")
        print(f"│  type: {desc}")
        print(f"│  P_sig={t.p_sig_input} | émotion={t.emotion_understood} "
              f"(conf LCT={t.confidence_ratis})")
        print(f"│  route={t.route} | status={t.status}")
        if t.confidence_needle is not None:
            print(f"│  Needle conf={t.confidence_needle} | certifié={t.confidence_certified}")
        print(f"│  ZK hash: {t.response_hash} (certifié={t.certified})")
        print(f"│  réponse: {t.response}")
        print(f"└─ {t.latency_ms}ms")

    # ── Invariance ZK ───────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("Invariance ZK (loi LCT) :")
    print("=" * 72)
    zk = agent.verify_zk_invariance("hello world how are you")
    print(f"  message : {zk['message']}")
    print(f"  hash joie   = {zk['hash_joie']}")
    print(f"  hash colère = {zk['hash_colère']}")
    print(f"  invariant : {'OUI ✓' if zk['invariant'] else 'NON ✗'}")
    print(f"  {zk['loi_LCT']}")

    # ── TTS ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("TTS (synthèse vocale) :")
    print("=" * 72)
    if tts.available():
        path = tts.speak_to_file("I am RATIS, a sovereign cognitive agent.")
        print(f"  moteur : {tts.engine_name()}")
        print(f"  fichier: {path}")
    else:
        print(f"  {tts.engine_name()} (installez espeak-ng pour le TTS offline)")

    # ── Sauvegarde des preuves ──────────────────────────────────────────────
    proofs = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agent": "RATIS-Fusion-stark-",
        "ttf_compute": agent.ratis.ttf_available,
        "n_tools": len(agent.tools),
        "tts_engine": tts.engine_name(),
        "zk_invariance": zk,
        "cases": results,
    }
    out = _ROOT / "proofs" / "fusion_demo_results.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(proofs, f, indent=2, default=str)
    print(f"\nPreuves sauvegardées : {out}")

    # ── Bilan ───────────────────────────────────────────────────────────────
    certified = sum(1 for r in results if r["status"] == "CERTIFIÉ")
    rejected = sum(1 for r in results if r["status"] == "REJETÉ")
    derived = sum(1 for r in results if r["status"] == "DÉRIVE")
    print(f"\nBilan : {certified} certifiés, {derived} dérive, {rejected} rejetés "
          f"(sur {len(results)} cas)")
    print(f"ZK invariance : {'VALIDÉ ✓' if zk['invariant'] else 'ÉCHEC ✗'}")
    print("=" * 72)


if __name__ == "__main__":
    main()
