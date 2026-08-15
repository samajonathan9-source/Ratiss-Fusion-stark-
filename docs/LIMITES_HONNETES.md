# docs/LIMITES_HONNETES.md — Limites franches de RATIS-Fusion-stark-

Honnêteté scientifique : on documente les échecs et les limites, pas seulement
les succès. Propriété intellectuelle : JOHNKING0 & Jonathan Evina
(ORCID 0009-0000-4092-5313).

---

## 1. Needle n'est PAS un générateur de langage naturel

**Découverte vérifiée.** Le document technique initial (Mistral) présentait
Needle comme un moteur de génération de langage fluide. En réalité, Needle 2
est un **tool-caller** : il n'y a **pas de free-text fallback**. Toute réponse
est un appel de fonction. Une requête qu'aucun outil déclaré ne peut servir
est refusée par l'appel vide `[]`.

**Conséquence pour la symbiose :**
- Needle gère l'**action structurée** (tool-calling, extraction JSON) — c'est
  sa vraie compétence, et elle est excellente (3/3 tool-calls certifiés).
- La **parole émotionnelle** reste assurée par le **décodeur RATIS** (bigramme
  beam), qui est rudimentaire (« it's it's too bad then go »).
- La génération de langage naturel riche nécessitera soit un fine-tuning LCT
  de Needle (Phase 4, expérimental), soit une base plus légère (Jonathan
  recherche une alternative).

## 2. Le filtre P_sig est trop indulgent (tokenizer de caractères)

**Hypothèse H2 ÉCHEC (documentée).** Le filtre anti-hallucination par P_sig
ne rejette pas assez le bruit aléatoire :

| Message | P_sig |
|---|---|
| you are amazing and funny | 0.977 |
| i feel so lonely and lost | 0.986 |
| asdfghjkl qqqq zzzz | 0.849 |
| qwerty asdf zxcv | 0.986 |

**Cause racine :** la cohérence topologique est calculée via la similarité
cosinus des signatures topologiques de caractères. Le bruit aléatoire utilise
les mêmes caractères répétés → signatures similaires → P_sig élevé.

**Borne connue** (héritée de Ratiss-experimental-IA-) : le tokenizer
topologique de caractères ne distingue pas les concepts abstraits
(quantum ≈ amour). Améliorer le tokenizer pour capturer le sens, pas juste
la forme des caractères, est une piste ouverte.

## 3. La persistance H1 d'un message court est nulle

**Borne technique.** La loi LCT définit R = P_sig = persistance du cycle H1
le plus long. Mais un message court (5 mots × nuage de points) ne forme
presque jamais de cycle H1 → P_sig = 0 pour tous les messages.

**Workaround honnête :** on utilise un **proxy** de cohérence (H0 + similarité
inter-mots), pas la persistance H1 stricte. C'est documenté dans le code
(`_message_coherence`). Ce n'est PAS la loi LCT elle-même (figée), c'est un
filtre d'entrée pragmatique pour l'anti-hallucination.

## 4. Le hash topo n'est PAS invariant sous paraphrase

**Hypothèse H5 ÉCHEC (documentée).**

| Message | Hash pensée |
|---|---|
| you are amazing | 64f2dbffa1378332 |
| you are wonderful | 2ff8919caa7e41a0 |

**Cause :** le hash topologique encode la **topologie exacte** (caractères,
structure), pas le **sens**. Deux synonymes ont des topologies différentes.

**Ce qui EST invariant (H4 VALIDÉ) :** le hash de la pensée est invariant sous
changement d'**énergie** (environnement thermo). On certifie la forme, pas le
courant — c'est la loi LCT.

## 5. La confiance Needle de base est basse (modèle non fine-tuné)

**Observation.** Sur les outils cliniques déclarés, Needle de base (sans
fine-tuning) donne une confiance de 0.10–0.34. Cela déclenche des statuts
DÉRIVE, ce qui est **le comportement anti-hallucination attendu** (on ne
certifie pas à l'aveugle), mais limite l'utilité pratique.

**Solution :** fine-tuning LoRA de Needle sur les outils (Phase 4), ou
déclaration d'outils mieux décrits.

## 6. Latence CPU du cerveau TTF-Compute

**Observation.** Le calcul TTF-Compute (cerveau AEON) ajoute jusqu'à 15–20s
sur certains messages (oscillation + MCB). Acceptable pour l'interaction
humaine, pas pour du temps réel. Le fallback sans TTF (topo signature) est
rapide (<1s) mais moins expressif.

## 7. Pas d'apprentissage conjoint bout-en-bout

**Limite d'architecture.** RATIS et Needle sont deux modules séparés. RATIS
filtre et certifie, Needle exécute. On ne met pas encore à jour les poids de
Needle par la loi LCT. La Phase 4 (LCT vs LoRA) est expérimentale et peut
échouer — la loi LCT échoue sur les NN entraînés par gradient (poids concentrés
≠ distribués). Needle étant un réseau d'attention, il faudra vérifier si sa
structure est assez distribuée.

## 8. GITHUB_TOKEN sans scope repo

**Limite process.** Le token GitHub de Jonathan n'a pas le scope `repo` : la
création de nouveaux dépôts est impossible via API. Jonathan les crée
manuellement. Les push se font sur branche + PR, jamais sur main.

## 9. Crédits QPU IBM presque épuisés

**Hors-scope ici.** Ce dépôt est CPU-only. Aucun appel QPU. Les crédits IBM
sont économisés pour les tests AEON critiques.
