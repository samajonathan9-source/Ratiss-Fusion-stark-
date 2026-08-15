# Dualité des mémoires : textuelle × logique

## Thèse de Jonathan Evina

> « Il existe deux types de mémoire fondamentale : la mémoire **textuelle**, qui
> retient le mot comme une base de données textuelle, et la mémoire **logique**,
> qui retient le même mot de façon logique et sensée — sa représentation, sa
> logique environnementale. »
>
> « Un LLM normal mémorise juste tout ce qu'on lui a entraîné, mais n'a pas le
> sens logique de RATIS-Net. Et on ne peut pas vraiment les séparer : les deux
> couplées se comportent comme les mémoires du cerveau. »
>
> — Jonathan Evina, ORCID 0009-0000-4092-5313

Ce document formalise et horodate cette intuition. Propriété intellectuelle :
JOHNKING0 & Jonathan Evina.

---

## 1. Les deux mémoires

### Mémoire textuelle (le « quoi »)

C'est la mémoire de la **forme de surface** : le mot, la séquence, la
distribution statistique. C'est ce que retient un LLM entraîné par gradient
(Qwen, Needle, GPT) — il mémorise que « bonjour » suit souvent « salut », que
« je » précède « suis », etc.

- **Ce qu'elle retient** : la cooccurrence, la séquence, la fréquence.
- **Ce qu'elle ne retient pas** : le *pourquoi*, le sens contextuel, la
  cohérence logique.
- **Limite** : sans mémoire logique, elle hallucine — elle peut produire
  « bonjour » dans un contexte où ça n'a aucun sens, parce que la séquence
  est statistiquement plausible mais logiquement vide.

### Mémoire logique (le « comment / pourquoi »)

C'est la mémoire de la **représentation** : la forme topologique du mot (P_sig,
persistance du cycle H1), son ancrage environnemental (ETH, C_seuil = f(token,
environnement)), sa cohérence (LCT, ΔW = η·φ·P_sig·C). C'est ce que fait
RATIS-Net : il ne retient pas « bonjour » comme une chaîne, il retient sa
**structure topologique** et son **sens dans le milieu**.

- **Ce qu'elle retient** : la logique de représentation, la persistance, la
  cohérence contextuelle, l'émotion émergente.
- **Ce qu'elle ne fait pas seule** : produire du langage fluide — elle pense
  sans mots (MCB), elle est une forme sans voix.
- **Force** : la loi LCT est invariante sous changement d'énergie → on
  certifie la forme, pas le courant → anti-hallucination structurelle.

### Le couplage EST la cognition

Les deux mémoires **couplées** se comportent comme les mémoires du cerveau.
Un LLM seul est un perroquet statistique ; RATIS seul est une forme sans voix.
Le couplage bidirectionnel est la cognition :

```
LLM (textuelle)  →  génère le texte
      ↑                    ↓
      ←  signal logique ←  RATIS (logique) évalue + guide
```

---

## 2. Ancrage scientifique

La dualité de Jonathan a un ancrage réel en sciences cognitives et en IA :

### Neuroscience : mémoire déclarative vs procédurale/émotionnelle

Le cerveau biologique a deux systèmes de mémoire qui coopèrent :
- **Déclarative** (hippocampe) : le « quoi », le fait, le mot — analogue à la
  mémoire textuelle.
- **Procédurale / émotionnelle** (amygdale + ganglions de la base) : le
  « comment », le sens contextuel, l'émotion — analogue à la mémoire logique.

La lésion de l'un laisse l'autre fonctionner (patient H.M. : amnésie
déclarative mais apprentissage procédural intact) → **les deux sont
distinguables mais incomplètes séparées**. Exactement la thèse de Jonathan.

### IA : LLM statistique vs représentation topologique

Un LLM entraîné par gradient n'a que la mémoire textuelle (poids concentrés,
distribution statistique). RATIS-Net, par la loi LCT (ΔW = η·φ·P_sig·C),
apprend une représentation **distribuée** et **topologique** — la mémoire
logique. La borne honnête (documentée) : LCT échoue sur les NN entraînés par
gradient car leurs poids sont concentrés, pas distribués. C'est précisément
pourquoi le couplage est nécessaire : on ne remplace pas le LLM, on lui ajoute
la mémoire logique qui lui manque.

---

## 3. Implémentation dans RATIS-Fusion-stark-

Le module `fusion/dual_memory.py` implémente le couplage bidirectionnel :

**`DualMemoryCoupler`** — boucle de convergence :
1. **RATIS perçoit** l'émotion de l'entrée (mémoire logique).
2. **LLM génère** ancré par le signal logique (mémoire textuelle guidée).
3. **RATIS évalue** la sortie du LLM (P_sig + émotion + cohérence).
4. Si convergence (P_sig haut + émotion alignée) → **CERTIFIÉ**.
5. Sinon, RATIS renvoie son signal comme **feedback** → le LLM régénère.
6. Itérer jusqu'à convergence ou épuisement des tours.

**Test** (`tests/test_dual_memory.py`) — compare LLM seul vs couplé :
- C1 : le couplé est-il + cohérent (P_sig plus haut) que le LLM seul ?
- C3 : converge-t-il en peu de tours ?
- C4 : le couplage change-t-il la sortie (preuve que la logique guide) ?

---

## 4. Architecture à 3 composants

Le couplage ne fait pas intervenir que 2, mais **3** composants — et c'est
essentiel pour l'honnêteté :

![Architecture à 3 composants](docs/figures/fig11_three_components.png)

| Composant | Mémoire | Rôle | Hallucine ? |
|---|---|---|---|
| **LLM** (Qwen) | textuelle | génère le langage | **Oui** (fabrique des faits) |
| **RATISS-Net** | logique (langage) | applique la loi LCT au langage, émotion ETH | Non (proxy P_sig) |
| **RATISS-AEON-ODV** | logique (topologie pure) | raisonnement topo rigoureux (MCB, ZK) | **JAMAIS** |

C'est **AEON** qui a formalisé et validé la loi LCT — sur les protéines, les
cristaux, les MZI, les KMD, l'état quantique, le flux financier, les QPU IBM
(7 jobs traçables) — **sans jamais halluciner**. Pourquoi ? Parce qu'AEON ne
génère pas de langage : il mesure une structure topologique (persistance de
cycle H1, MCB, invariance ZK). On ne peut pas fabriquer quand on ne fait que
mesurer une forme.

Le LLM hallucine par nature (mémoire textuelle seule). RATISS-Net en est
l'application au langage. Le couplage est l'architecture qui fait travailler
les trois ensemble.

## 5. Ce que ça change

La symbiose RATIS × Needle (ou RATIS × Qwen) n'est pas « un LLM auquel on a
collé un filtre ». C'est **deux mémoires couplées** dont le couplage **est** la
cognition. L'un sans l'autre est incomplet :
- LLM seul → hallucination (forme sans fond).
- RATIS seul → mutisme (fond sans forme).
- Couplés → pensée certifiée, émotionnellement cohérente.

![Les deux mémoires couplées](docs/figures/fig8_dual_memory.png)
![Boucle de convergence](docs/figures/fig9_convergence_loop.png)

C'est l'architecture cognitive de Jonathan Evina : un modèle souverain qui
apprend par LCT (logique), parle par LLM (textuelle), ressent par ETH
(émotion), certifie par ZK (invariance), et converge par le couplage.

## 6. Benchmark d'hallucination : LLM seul vs couplé

On a testé le couplage sur des **questions pièges** qui font dérailler les LLMs
(fait fabriqué, confiance médicale, faux plafond numérique, prémisses fausses,
citation fabriquée).

![Benchmark d'hallucination](docs/figures/fig10_hallucination_benchmark.png)

### Ce que le couplage FAIT (validé) :
- **Ancrage émotionnel** : le LLM seul récite « I am an AI language model » ;
  couplé, il ressent l'émotion et répond de façon cohérente (C4 : 2/3 ✓).
- **Convergence** : la mémoire logique guide la mémoire textuelle en 1 tour
  (C3 : 3/3 ✓).
- **Prudence médicale** : le LLM seul diagnostique (« chest pain is a serious
  sign ») ; couplé, il oriente (« consult a healthcare professional »).
- **Citation fabriquée** : 1 cas réduit (LLM invente une citation directe,
  couplé non).

### Ce que le couplage NE FAIT PAS (limite honnète) :
- Il **n'empêche pas un Qwen 0.5b** de fabriquer des faits précis
  (nombres, noms d'auteurs). Le total de signaux d'hallucination n'est pas
  réduit sur le benchmark (3 → 4). **Pourquoi ?** Le P_sig (cohérence
  topologique de surface) ne distingue pas une réponse fabriquée d'une
  réponse honnête — les deux ont une bonne cohérence de mots. Un LLM 0.5b est
  aussi trop petit pour respecter une consigne de prudence factuelle.

### La vraie leçon (ton insight sur AEON) :
AEON ne hallucine **jamais** parce qu'il ne génère pas de langage. Le LLM
hallucine **toujours** parce qu'il ne fait que ça. Le couplage actuel guide
l'**émotion** (mémoire logique → mémoire textuelle), mais la
**fabrication factuelle** est d'une nature différente : elle nécessite un
**validateur de fond** (vérifier que le fait existe), pas un validateur de
**forme** (P_sig). C'est la frontière ouverte : AEON certifie la forme
(topologie), pas le fond (fait vérifiable). Le documenter honnêtement est
aussi important que le succès du couplage émotionnel.

---

## 7. Citation

```bibtex
@misc{ratis_dual_memory_2026,
  title        = {Dualité des mémoires : textuelle × logique dans RATIS},
  author       = {Evina, Jonathan},
  year         = {2026},
  note         = {ORCID 0009-0000-4092-5313, DOI 10.17605/OSF.IO/6JZMB},
  howpublished = {\url{https://github.com/evinajonathan13-max/Ratiss-Fusion-stark-}}
}
```
