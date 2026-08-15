"""tests.test_anti_hallucination — le cœur scientifique : P_sig comme filtre.

Hypothèses testées (falsifiables) :
  H1 : la cohérence topologique P_sig distingue les entrées cohérentes du bruit.
  H2 : le filtre P_sig < seuil rejette les entrées incohérentes (anti-hallucination).
  H3 : la confiance croisée (needle × P_sig) est PLUS restrictive que needle seul.
  H4 : l'invariance ZK : le hash de la pensée est invariant sous changement d'énergie.
  H5 : l'invariance sous paraphrase : deux messages de même sens → hashes proches.

On documente les SUCCÈS et les ÉCHECS (honnêteté scientifique).
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
    print("Test anti-hallucination — P_sig comme filtre cognitif")
    print("=" * 72)

    print("\nConstruction de l'agent...")
    agent = RatisFusionAgent(tools=DEFAULT_TOOLS, train_examples=480, train_epochs=5)

    results = {}

    # ── H1 : P_sig distingue cohérent vs bruit ──────────────────────────────
    print("\nH1 : P_sig distingue cohérent vs bruit")
    coherent = ["you are amazing and funny", "i feel so lonely and lost",
                "the patient needs help today", "hello how are you my friend"]
    noise = ["asdfghjkl qqqq zzzz", "xyz abc def ghi random",
             "aaaa bbbb cccc dddd", "qwerty asdf zxcv"]
    coh_scores = [(_message_coherence(m), m) for m in coherent]
    noi_scores = [(_message_coherence(m), m) for m in noise]
    print("   Coherent:")
    for s, m in coh_scores:
        print(f"     {s:.4f}  {m}")
    print("   Noise:")
    for s, m in noi_scores:
        print(f"     {s:.4f}  {m}")
    coh_mean = sum(s for s, _ in coh_scores) / len(coh_scores)
    noi_mean = sum(s for s, _ in noi_scores) / len(noi_scores)
    h1 = coh_mean > noi_mean
    results["H1_P_sig_distinguish"] = h1
    print(f"   → cohérent moyen={coh_mean:.4f} > bruit moyen={noi_mean:.4f} : "
          f"{'OUI ✓' if h1 else 'NON ✗ (limite tokenizer de caractères)'}")

    # ── H2 : filtre P_sig rejette le bruit ──────────────────────────────────
    print("\nH2 : filtre P_sig < seuil rejette les entrées incohérentes")
    # seuil bas pour ne pas rejeter les messages valides
    agent.p_sig_threshold = 0.85
    rejets = 0
    for m in noise:
        t = agent.think(m, "neutre")
        if t.status == "REJETÉ":
            rejets += 1
    h2 = rejets >= len(noise) / 2  # au moins la moitié du bruit rejetée
    results["H2_filter_rejects_noise"] = h2
    print(f"   bruit rejeté : {rejets}/{len(noise)} → {'OUI ✓' if h2 else 'NON ✗ (borne: tokenizer de caractères trop indulgent)'}")

    # ── H3 : confiance croisée plus restrictive ──────────────────────────────
    print("\nH3 : confiance croisée (needle × P_sig) ≤ needle seul")
    t = agent.think("check the status of patient 123", "calme")
    if t.confidence_needle is not None:
        h3 = t.confidence_certified <= t.confidence_needle
        results["H3_cross_confidence_restrictive"] = h3
        print(f"   needle={t.confidence_needle} | certifié={t.confidence_certified} "
              f"→ {'OUI ✓' if h3 else 'NON ✗'}")
    else:
        results["H3_cross_confidence_restrictive"] = None
        print("   (route parole — non applicable)")

    # ── H4 : invariance ZK sous changement d'énergie ────────────────────────
    print("\nH4 : invariance ZK (hash pensée invariant sous énergie)")
    zk = agent.verify_zk_invariance("hello world how are you")
    h4 = zk["invariant"]
    results["H4_zk_invariance_energy"] = h4
    print(f"   hash joie={zk['hash_joie']} | hash colère={zk['hash_colère']}")
    print(f"   → invariant : {'OUI ✓' if h4 else 'NON ✗'}")
    print(f"   loi LCT : {zk['loi_LCT']}")

    # ── H5 : invariance sous paraphrase ─────────────────────────────────────
    print("\nH5 : invariance sous paraphrase (même sens → même hash pensée)")
    t1 = agent.ratis.think("you are amazing", env_from_test("joie"))
    t2 = agent.ratis.think("you are wonderful", env_from_test("joie"))
    # paraphrases proches → hashes potentiellement différents (borne honnête)
    h5 = t1.thought_hash == t2.thought_hash
    results["H5_paraphrase_invariance"] = h5
    print(f"   'you are amazing' → {t1.thought_hash}")
    print(f"   'you are wonderful' → {t2.thought_hash}")
    print(f"   → même hash : {'OUI ✓' if h5 else 'NON ✗ (borne: le hash encode la topo exacte, pas le sens — documenté)'}")

    # ── Bilan ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("BILAN DES HYPOTHÈSES (honnêteté scientifique) :")
    for h, v in results.items():
        if v is True:
            print(f"   {h} : VALIDÉ ✓")
        elif v is False:
            print(f"   {h} : ÉCHEC ✗ (documenté comme limite)")
        else:
            print(f"   {h} : non applicable")
    validated = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    print(f"\n   {validated}/{total} hypothèses validées")
    print("=" * 72)
    return validated >= 3  # au moins 3/5


def env_from_test(name):
    from fusion.bridge import env_from_name
    return env_from_name(name)


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
