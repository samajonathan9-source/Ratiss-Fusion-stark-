"""tests.test_bridge — test du pont cognitif RATIS × Needle.

Valide le pipeline symbiotique :
  1. La boucle cognitive fonctionne (cognition RATIS + action Needle).
  2. Le router distingue action (Needle) vs parole (décodeur RATIS).
  3. La confiance croisée (needle × P_sig) est calculée.
  4. La certification ZK (hash topo) est produite.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from fusion.bridge import RatisFusionAgent, _message_coherence
from tools.clinical_tools import DEFAULT_TOOLS


def main():
    print("=" * 72)
    print("Test du bridge symbiotique RATIS × Needle")
    print("=" * 72)

    print("\n1. Construction + entraînement du cerveau RATIS...")
    t0 = time.time()
    agent = RatisFusionAgent(tools=DEFAULT_TOOLS, train_examples=480, train_epochs=5)
    print(f"   agent prêt en {time.time()-t0:.1f}s")
    print(f"   TTF-Compute (penser) : {agent.ratis.ttf_available}")
    print(f"   Outils Needle (corps): {len(agent.tools)}")

    # ── Test 2 : router action vs parole ────────────────────────────────────
    print("\n2. Router (action vs parole) :")
    cases = [
        ("check the status of patient 123", "calme", "action"),
        ("you are amazing and funny", "joie", "parole"),
        ("check the availability of therapy room", "neutre", "action"),
        ("i feel so lonely and lost", "peur", "parole"),
    ]
    router_ok = 0
    for msg, env, expected in cases:
        t = agent.think(msg, env)
        ok = t.route == expected
        router_ok += ok
        mark = "✓" if ok else "✗"
        print(f"   {mark} [{env}] '{msg}' → route={t.route} (attendu={expected})")
        print(f"      status={t.status} P_sig={t.p_sig_input} conf_cert={t.confidence_certified}")
        print(f"      response: {t.response[:80]}")
    print(f"   Router : {router_ok}/{len(cases)}")

    # ── Test 3 : confiance croisée ──────────────────────────────────────────
    print("\n3. Confiance croisée (needle × P_sig) :")
    t = agent.think("check the status of patient 456", "calme")
    print(f"   P_sig_input     = {t.p_sig_input}")
    print(f"   confidence_needle = {t.confidence_needle}")
    print(f"   confidence_certified = {t.confidence_certified}")
    if t.confidence_needle is not None:
        expected = round(t.confidence_needle * t.p_sig_input, 4)
        ok = abs(t.confidence_certified - expected) < 0.01
        print(f"   {'✓' if ok else '✗'} confiance croisée = needle × P_sig = {expected}")
    else:
        print("   (route parole — confiance = conf_ratis × P_sig)")

    # ── Test 4 : certification ZK ───────────────────────────────────────────
    print("\n4. Certification ZK (hash topo) :")
    t = agent.think("you are amazing and funny", "joie")
    print(f"   response_hash = {t.response_hash}")
    print(f"   certified     = {t.certified}")
    print(f"   thought_hash  = {t.thought_hash}")
    ok = len(t.response_hash) == 16 and t.certified
    print(f"   {'✓' if ok else '✗'} hash ZK 16-char + certifié")

    print("\n" + "=" * 72)
    total = router_ok + (1 if ok else 0)
    print(f"BILAN : {total}/{len(cases)+1} vérifications passées")
    print("=" * 72)
    return total == len(cases) + 1


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
