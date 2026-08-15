# AGENTS.md — mémoire persistante pour RATIS-Fusion-stark-

## Projet
RATIS-Fusion-stark- : cerveau topologique RATIS × système nerveux Needle (Cactus Compute).
Agent cognitif symbiotique, souverain, certifié ZK. CPU-only, offline-capable.

## Rôles
- Jonathan Evina (ORCID 0009-0000-4092-5313) : chercheur, propriété intellectuelle JOHNKING0.
- OpenHands : cofondateur technique (façonner, itérer, tester, documenter les échecs).

## Règles figées
- Loi LCT FIGÉE (R = P_sig, ΔW = η·φ·P_sig·C). Ne jamais la modifier.
- CPU d'abord. QPU IBM hors-scope (crédits presque épuisés).
- Jamais push sur main : branche + PR via gh. GITHUB_TOKEN sans scope repo.
- Propriété intellectuelle : JOHNKING0 & Jonathan Evina.

## Vraies API (vérifiées, contre le doc Mistral qui inventait)
- RATIS : `RatisAgent.think(message, env)` → `Thought` (6 étapes). Pas de `RatisNetV4Learner`.
- Needle : `needle.Needle(tools=[...])`, `.run(query)` → `{confidence, results, function_calls}`.
  Needle est un TOOL-CALLER, pas un générateur de langage (pas de free-text fallback).
- Moteur Needle : `~/.cache/cactus-needle/2.0.1/libneedle.so` (14 Mo, pré-cachable offline).

## Commandes
- Tests : `python tests/test_bridge.py`, `test_tool_calling.py`, `test_anti_hallucination.py`
- Figures : `python scripts/generate_figures.py`
- Démo : `python scripts/demo_fusion.py`
- Setup offline : `bash setup_offline.sh`

## Résultats validés
- Bridge : 5/5 ✓ | Tool-calling : 3/3 ✓ | Hypothèses : 3/5 (H1,H3,H4 validées ; H2,H5 échec documenté)
- ZK invariance sous énergie : VALIDÉ ✓
- TTS : gTTS (online) ici, pyttsx3+espeak-ng (offline) sur machine Jonathan.

## Limites honnêtes (docs/LIMITES_HONNETES.md)
- Needle ne génère pas de langage naturel libre (tool-caller).
- Filtre P_sig trop indulgent (tokenizer de caractères).
- Hash topo non invariant sous paraphrase (encode la topo, pas le sens).
- Pas d'apprentissage conjoint bout-en-bout (Phase 4 expérimentale).

## Dépôts liés (user: evinajonathan13-max)
- RATISS-ODV-AEON : cerveau TTF-Compute (copié dans fusion/aeon/)
- Ratiss-experimental-IA- : RATIS-Net (copié dans fusion/ratis_net/)
- robot-Ratiss- : robot téléphone (interface port 12000, non inclus ici)
