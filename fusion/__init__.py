"""fusion — RATIS-Fusion-stark : cerveau topologique RATIS × système nerveux Needle.

Symbiose cognitive :
  - RATIS (cerveau) : perçoit (topologie), pense (TTF/MCB), ressent (ETH émotion),
    comprend (loi LCT, figée), certifie (ZK, hash topo invariant).
  - Needle (corps) : tool-calling structuré + extraction JSON, exécute l'action.

La loi LCT (R = P_sig, ΔW = η·φ·P_sig·C) est FIGÉE — elle gouverne la cognition,
jamais modifiée. Needle ne remplace pas la cognition, il exécute l'action que la
cognition autorise.

Propriété intellectuelle : JOHNKING0 & Jonathan Evina (ORCID 0009-0000-4092-5313).
"""
from .bridge import RatisFusionAgent, FusionThought
from .tts import OfflineTTS

__all__ = ["RatisFusionAgent", "FusionThought", "OfflineTTS"]
