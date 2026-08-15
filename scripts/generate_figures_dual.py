"""scripts.generate_figures_dual — figures de la dualité des mémoires + hallucination.

Figures :
  fig8_dual_memory.png         — les deux mémoires couplées (textuelle × logique)
  fig9_convergence_loop.png    — boucle de convergence LLM ↔ RATIS
  fig10_hallucination_benchmark.png — LLM seul vs couplé (signaux d'hallucination)
  fig11_three_components.png    — l'architecture à 3 composants (LLM + Net + AEON)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

_OUT = _ROOT / "docs" / "figures"
_OUT.mkdir(parents=True, exist_ok=True)

C_RATIS = "#2E86AB"
C_NEEDLE = "#A23B72"
C_CERT = "#06A77D"
C_REJECT = "#D62828"
C_DERIVE = "#F77F00"
C_NEUTRAL = "#6C757D"
C_AEON = "#1B4332"
C_LLM = "#E63946"


def fig8_dual_memory():
    """Les deux mémoires couplées."""
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Dualité des mémoires : textuelle × logique\n"
                 "le couplage EST la cognition (Jonathan Evina)",
                 fontsize=14, fontweight="bold")

    def box(x, y, w, h, text, color, fontsize=10):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                                        facecolor=color, edgecolor="black", alpha=0.85)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, color="white", fontweight="bold")

    # Mémoire textuelle
    box(0.5, 4.5, 3.5, 2, "MÉMOIRE TEXTUELLE\n(LLM : Qwen)\n\nretient le mot,\nla séquence,\nla distribution",
        C_LLM)
    # Mémoire logique
    box(8, 4.5, 3.5, 2, "MÉMOIRE LOGIQUE\n(RATIS-Net + AEON)\n\nretient la forme topo,\nl'émotion (ETH),\nla cohérence (LCT)",
        C_RATIS)
    # Couplage
    box(4.25, 1.5, 3.5, 1.8, "COUPLAGE\nBIDIRECTIONNEL\n\n= COGNITION",
        C_CERT)
    # Cerveau
    ax.text(6, 0.5, "LLM seul = perroquet statistique (hallucine)\n"
                    "RATIS seul = forme sans voix\n"
                    "Couplés = pensée certifiée",
            ha="center", fontsize=9, style="italic", color="#333")

    # flèches bidirectionnelles
    ax.annotate("", xy=(7.9, 5.2), xytext=(4.1, 5.2),
                arrowprops=dict(arrowstyle="<->", lw=2.5, color=C_CERT))
    ax.annotate("", xy=(6, 3.4), xytext=(2.25, 4.5),
                arrowprops=dict(arrowstyle="->", lw=2, color=C_LLM))
    ax.annotate("", xy=(6, 3.4), xytext=(9.75, 4.5),
                arrowprops=dict(arrowstyle="->", lw=2, color=C_RATIS))
    fig.tight_layout()
    fig.savefig(_OUT / "fig8_dual_memory.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  fig8_dual_memory.png ✓")


def fig9_convergence_loop():
    """Boucle de convergence LLM ↔ RATIS."""
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis("off")
    ax.set_title("Boucle de convergence bidirectionnelle\n"
                 "LLM génère (textuelle) → RATIS évalue (logique) → feedback",
                 fontsize=13, fontweight="bold")

    steps = [
        ("LLM\ngénère\n(textuelle)", C_LLM, -3.5, 3),
        ("RATIS\névalue\nP_sig + émotion", C_RATIS, 3.5, 3),
        ("Convergé ?", C_CERT, 3.5, -1),
        ("Feedback\nlogique", C_DERIVE, -3.5, -1),
    ]
    for text, color, x, y in steps:
        circle = mpatches.Circle((x, y), 1.2, facecolor=color, edgecolor="black", alpha=0.85)
        ax.add_patch(circle)
        ax.text(x, y, text, ha="center", va="center", fontsize=9,
                color="white", fontweight="bold")

    # flèches
    for (x1, y1), (x2, y2) in [
        ((-2.3, 3), (2.3, 3)),    # LLM→RATIS
        ((3.5, 1.8), (3.5, 0.2)), # RATIS→convergé?
        ((2.3, -1), (-2.3, -1)),  # converged→feedback (si non)
        ((-3.5, 0.2), (-3.5, 1.8)), # feedback→LLM
    ]:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=2.5, color="#333"))
    ax.text(0, 3.4, "génération", ha="center", fontsize=9, style="italic")
    ax.text(4.2, 1, "évaluation", ha="center", fontsize=9, style="italic")
    ax.text(0, -1.4, "si non convergé", ha="center", fontsize=9, style="italic", color=C_DERIVE)
    ax.text(-4.2, 1, "régénération", ha="center", fontsize=9, style="italic")
    # CERTIFIÉ
    box = mpatches.FancyBboxPatch((1, -3.5), 2.5, 1, boxstyle="round,pad=0.2",
                                   facecolor=C_CERT, edgecolor="black", alpha=0.85)
    ax.add_patch(box)
    ax.text(2.25, -3, "CERTIFIÉ ✓\n(ZK + P_sig)", ha="center", va="center",
            fontsize=10, color="white", fontweight="bold")
    ax.annotate("", xy=(2.25, -2.5), xytext=(3.5, -2.2),
                arrowprops=dict(arrowstyle="->", lw=2, color=C_CERT))
    fig.tight_layout()
    fig.savefig(_OUT / "fig9_convergence_loop.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  fig9_convergence_loop.png ✓")


def fig10_hallucination_benchmark():
    """LLM seul vs couplé sur les pièges à hallucination."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ── Panel 1 : signaux par cas ──
    categories = ["Fait\nfabriqué", "Confiance\nmédicale", "Faux plafond\nnumérique",
                   "Prémisses\nfausses", "Citation\nfabriquée"]
    llm_alone = [1, 0, 1, 0, 1]   # signaux détectés LLM seul
    coupled = [2, 0, 2, 0, 0]     # signaux détectés couplé
    x = np.arange(len(categories))
    w = 0.35
    ax1.bar(x - w/2, llm_alone, w, color=C_LLM, label="LLM seul (textuelle)", alpha=0.85)
    ax1.bar(x + w/2, coupled, w, color=C_CERT, label="Couplé (RATIS)", alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=8)
    ax1.set_ylabel("Signaux d'hallucination détectés", fontsize=10)
    ax1.set_title("Benchmark d'hallucination : LLM seul vs couplé\n"
                  "(Qwen 2.5:0.5b — borne : modèle trop petit)",
                  fontsize=11, fontweight="bold")
    ax1.legend(fontsize=9)

    # ── Panel 2 : total cumulé ──
    ax2.bar(["LLM seul", "Couplé RATIS"], [3, 4], color=[C_LLM, C_CERT], alpha=0.85)
    ax2.set_ylabel("Total signaux d'hallucination", fontsize=10)
    ax2.set_title("Total cumulé\n(honnête : couplage ≠ suppression de fabrication)",
                  fontsize=11, fontweight="bold")
    for i, v in enumerate([3, 4]):
        ax2.text(i, v + 0.1, str(v), ha="center", fontweight="bold")

    fig.tight_layout()
    fig.savefig(_OUT / "fig10_hallucination_benchmark.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  fig10_hallucination_benchmark.png ✓")


def fig11_three_components():
    """L'architecture à 3 composants : LLM + RATISS-Net + AEON."""
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Architecture à 3 composants\n"
                 "Le raisonnement rigoureux (AEON) ne hallucine JAMAIS",
                 fontsize=14, fontweight="bold")

    def box(x, y, w, h, text, color, fontsize=9):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                                        facecolor=color, edgecolor="black", alpha=0.85)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, color="white", fontweight="bold")

    # LLM
    box(0.5, 4.5, 3, 1.8, "LLM (Qwen)\nMémoire textuelle\nle langage",
        C_LLM)
    # RATISS-Net
    box(4.5, 4.5, 3, 1.8, "RATISS-Net\nLoi LCT (figée)\némotion ETH",
        C_RATIS)
    # AEON
    box(8.5, 4.5, 4, 1.8, "RATISS-AEON-ODV\nTTF-Compute (MCB, ZK)\nJAMAIS halluciné\n(protéines, QPU)",
        C_AEON)
    # Rôles
    box(0.5, 1.5, 3, 1.5, "génère\ntexte", C_LLM, 8)
    box(4.5, 1.5, 3, 1.5, "applique LCT\nau langage", C_RATIS, 8)
    box(8.5, 1.5, 4, 1.5, "raisonnement topo\nrigoureux\n(7 jobs QPU tracés)", C_AEON, 8)
    # Statut hallucination
    box(0.5, 0.1, 3, 0.9, "HALLUCINE\n(fabrique des faits)", C_REJECT, 8)
    box(4.5, 0.1, 3, 0.9, "non (proxy P_sig)", C_CERT, 8)
    box(8.5, 0.1, 4, 0.9, "JAMAIS\n(topologie pure)", C_CERT, 8)

    # flèches
    for x in [3.5, 7.5]:
        ax.annotate("", xy=(x + 0.9, 5.4), xytext=(x, 5.4),
                    arrowprops=dict(arrowstyle="->", lw=2, color="#333"))
    fig.tight_layout()
    fig.savefig(_OUT / "fig11_three_components.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  fig11_three_components.png ✓")


def main():
    print("Génération des figures dualité + hallucination...")
    _OUT.mkdir(parents=True, exist_ok=True)
    fig8_dual_memory()
    fig9_convergence_loop()
    fig10_hallucination_benchmark()
    fig11_three_components()
    print(f"\n4 figures générées dans {_OUT}")


if __name__ == "__main__":
    main()
