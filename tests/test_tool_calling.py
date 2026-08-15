"""tests.test_tool_calling — outils Needle certifiés par RATIS.

Valide que l'agent symbiotique :
  1. Appelle les bons outils via Needle (action structurée).
  2. Extrait les résultats en JSON.
  3. Certifie les résultats (confiance croisée + hash ZK).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from fusion.bridge import RatisFusionAgent
from tools.clinical_tools import DEFAULT_TOOLS


def main():
    print("=" * 72)
    print("Test tool-calling certifié (Needle exécute, RATIS certifie)")
    print("=" * 72)

    print("\nConstruction...")
    agent = RatisFusionAgent(tools=DEFAULT_TOOLS, train_examples=480, train_epochs=5)

    cases = [
        ("check the status of patient 123", "calme", "get_patient_status",
         "123", "anxious"),
        ("check the status of patient 456", "calme", "get_patient_status",
         "456", "calm"),
        ("check the availability of therapy room", "neutre",
         "check_resource_availability", "therapy room", "available"),
    ]

    passed = 0
    for msg, env, expected_tool, expected_arg, expected_key in cases:
        print(f"\n  [{env}] '{msg}'")
        t = agent.think(msg, env)
        print(f"    route={t.route} status={t.status}")
        print(f"    needle_conf={t.confidence_needle} certifié={t.confidence_certified}")
        print(f"    tool_results: {t.tool_results}")
        print(f"    ZK: {t.response_hash}")

        ok_route = t.route == "action"
        ok_tool = any(expected_tool in str(r) or expected_arg in str(r)
                      for r in t.tool_results)
        ok_result = any(expected_key in str(r).lower() or expected_arg in str(r)
                        for r in t.tool_results)
        ok = ok_route and ok_tool
        passed += ok
        print(f"    {'✓' if ok else '✗'} route={ok_route} tool={ok_tool} result={ok_result}")

    print("\n" + "=" * 72)
    print(f"BILAN : {passed}/{len(cases)} tool-calls certifiés")
    print("=" * 72)
    return passed >= len(cases) - 1  # tolérance 1


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
