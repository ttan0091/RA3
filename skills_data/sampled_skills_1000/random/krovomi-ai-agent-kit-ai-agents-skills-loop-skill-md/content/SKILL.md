---
name: loop
description: Ralph Loop v2.0 - Développement itératif modulaire, optimisé en tokens
version: "2.0"
aliases: ["ralph", "iterate"]
---

# Ralph Loop v2.0

**Développement itératif IA modulaire, optimisé en tokens**. Fonctionne de manière autonome jusqu'à ce que les critères de complétion soient atteints avec **60% de réduction de tokens** grâce au chargement modulaire intelligent.

## 🚀 Nouveautés v2.0

- **Architecture modulaire** - Chargez uniquement ce dont vous avez besoin
- **Optimisation tokens** - 60% de réduction vs monolithique
- **Récupération intelligente** - Checkpoint automatique et reprise
- **Prompts ultra-efficaces** - Templates optimisés en tokens
- **Contexte adaptatif** - Compression dynamique basée sur l'utilisation des tokens

## Quand Utiliser

- Tâches nécessitant multiples passes de raffinement
- Développement style TDD
- Tâches complexes mais bien définies
- Quand vous voulez "partir" et laisser l'IA finir

## Utilisation

### Commandes de Base

```bash
# Mode minimal (core + completion) - ~1500 tokens
@loop "Corriger les tests échouants" --mode minimal

# Mode standard (core + prompts + completion) - ~2300 tokens  
@loop "Ajouter l'authentification utilisateur" --mode standard

# Mode récupération (core + recovery) - ~1300 tokens
@resume-loop --checkpoint-id abc123
```

### Alias

```bash
@ralph "Construire une API REST pour todos"
@iterate "Implémenter l'authentification utilisateur"
@resume-ralph checkpoint-123.json
```

### Sélection de Mode

| Mode | Cas d'Usage | Tokens | Modules Chargés |
|------|-------------|--------|----------------|
| **minimal** | Corrections rapides, tâches simples | ~1500 | core + completion |
| **standard** | Développement de fonctionnalités | ~2300 | core + prompts + completion |
| **recovery** | Reprise depuis checkpoint | ~1300 | core + recovery |

## Meilleures Pratiques de Prompts (v2.0)

### Structure Ultra-Compacte

```bash
TASK: Objectif en une ligne
MUST:
- Exigence 1
- Exigence 2  
- Exigence 3
DONE: <promise>COMPLETE</promise>
```

### Templates Optimisés en Tokens

**Minimal (200 tokens) :**
```bash
TASK: API auth JWT
MUST:
- POST /login + /register endpoints
- bcrypt password hashing
- JWT token generation/validation
DONE: <promise>COMPLETE</promise>
```

**Standard (400 tokens) :**
```bash
TASK: {{ feature_name }} fonctionnalité

REQUIREMENTS:
- {{ core_requirement }}
- Tests passants
- Pas d'erreurs de build

COMPLETION: <promise>COMPLETE</promise> quand tout est rempli

STUCK: Après 10 échecs, documenter les bloqueurs & suggérer simplifications
```

**Mode TDD (500 tokens) :**
```bash
TASK: {{ task }} (mode TDD)

CYCLE:
1. Écrire test échouant
2. Implémenter code minimum
3. Lancer test
4. Corriger/refactoriser jusqu'au vert
5. Répéter jusqu'à ce que toutes les exigences soient remplies

DONE: <promise>COMPLETE</promise>
```

## Détection de Complétion (Améliorée v2.0)

### Signaux Ultra-Efficaces

| Signal | Tokens | Confiance | Quand Utiliser |
|--------|--------|----------|----------------|
| `✓` | 1 | 0.9 | Complétion rapide |
| `OK` | 2 | 0.85 | Tâches simples |
| `FIN` | 3 | 0.9 | Tâches multi-étapes |
| `<done/>` | 7 | 1.0 | Complétion standard |
| `<promise>COMPLETE</promise>` | 22 | 1.0 | Tâches complexes |

### Méthodes de Détection

1. **Haute Confiance (immédiat) :**
   - `<promise>COMPLETE</promise>`
   - `<done/>`
   - `TASK_COMPLETE`

2. **Moyenne Confiance (nécessite validation) :**
   - `✅.*complete`
   - `all tests pass`
   - `implementation complete`

3. **Auto-Critères (validation système) :**
   - Build réussi
   - Tests passants (optionnel pour économiser des tokens)
   - Pas de nouveaux avertissements

## Gestion des Tokens (NOUVEAU v2.0)

### Compression de Contexte Adaptative

| Usage Tokens | Action | Contexte Préservé |
|---------------|--------|-------------------|
| **< 80%** | Opération normale | Contexte complet (2 itérations) |
| **80-90%** | Mode urgence | Dernier succès + bloqueurs actuels |
| **90-95%** | Mode critique | Tâche actuelle uniquement |
| **> 95%** | Checkpoint & pause | Sauvegarder état pour reprise |

### Stratégies de Récupération

```bash
# Niveau 1 (80% tokens) - Compresser le contexte
CONTEXT COMPRESSED: Travaille sur l'API auth.
Dernier progrès : endpoints terminés.
Problème actuel : 2 tests échouent.
Focus uniquement sur l'étape immédiate suivante.

# Niveau 2 (90% tokens) - Contexte minimal  
TASK: Corriger les tests auth échouants.
DO: Déboguer les échecs de tests.
OUTPUT: <promise>COMPLETE</promise> quand terminé.

# Niveau 3 (95% tokens) - Checkpoint & pause
Pour reprendre : @resume-loop --checkpoint-id abc123
État sauvegardé : fichiers_modifiés, statut_tests, iteration_actuelle
```

### Reprise Après Interruption

```bash
@resume-loop --checkpoint-id checkpoint-2024-01-26-abc123

# Sortie :
REPRISE Ralph Loop à l'itération 12.
Progrès jusqu'à présent : API auth 80% complète, 8/10 tests passants
Travail restant : Corriger 2 tests échouants, ajouter la validation d'entrée
Continuer là où nous nous sommes arrêtés...
```

## Suivi des Progrès (Amélioré)

Le loop suit :
- Fichiers modifiés par itération
- Tests passants delta  
- Couverture delta
- Avertissements build delta
- **Usage tokens par itération** (NOUVEAU)
- **Ratio compression contexte** (NOUVEAU)

**Détection de stagnation** : Si aucun progrès pendant 3+ itérations, des approches alternatives sont suggérées.

## Récupération de Blocage (Progressive)

| Itérations Bloquées | Action |
|-------------------|--------|
| 3 | Analyser les bloqueurs |
| 5 | Suggérer des alternatives |
| 8 | Réduire automatiquement la portée |
| 10 | Essayer une approche alternative |
| 12+ | Escalader à l'humain |

## Approches Alternatives (Auto-appliquées)

Quand bloqué, le loop peut essayer :

- **Simplifier** : Retirer la complexité, focus sur le cœur
- **Décomposer** : Diviser en sous-tâches plus petites
- **Stub d'abord** : Créner des stubs, puis implémenter un par un
- **Chemin heureux seulement** : Ignorer les cas limites temporairement

## Gestion du Contexte (Optimisé v2.0)

### Ce Qui Persiste Entre Itérations (MINIMAL)
- Fichiers modifiés
- Statut des tests  
- Statut du build
- **Résumé dernière itération seulement** (pas toutes les sorties)

### Ce Qui Reset Chaque Itération (AGRESSIF)
- Mémoire de travail
- Chemins d'exploration
- **Historique complet des itérations** (optimisation tokens)

### Limites de Contexte Adaptatives
- **Normal** : 4000 tokens max
- **Urgence** : 1000 tokens min
- **Critique** : 500 tokens réservés pour la récupération

## Intégration avec les Chains

Utiliser le mode Ralph Loop dans les chains :

```yaml
# Dans la définition de chain
mode: ralph-loop
max_iterations: 30
```

Ou déclencher automatiquement pour les tâches complexes.

## Conseils (Mis à jour v2.0)

1. **Choisir le bon mode** - Utiliser `--mode minimal` pour les corrections rapides
2. **Prompts ultra-compacts** = 60% d'économie de tokens
3. **Auto-checkpoints** - Le système sauve à 80%/90%/95% d'utilisation des tokens
4. **Signaux de complétion efficaces** - Utiliser `✓` (1 token) pour les tâches simples
5. **Surveiller l'utilisation des tokens** - Vérifier `@loop-status` pour la consommation actuelle
6. **Récupération transparente** - Tout progrès préservé dans les checkpoints

## Métriques (Améliorées v2.0)

Après complétion :
```bash
## Ralph Loop Terminé - Optimisé en Tokens

| Métrique | Valeur | Amélioration |
|--------|-------|-------------|
| Total Itérations | 12 | -20% vs v1.1 |
| Temps Écoulé | 8m 32s | -15% vs v1.1 |
| Fichiers Modifiés | 15 | Identique |
| Tests Ajoutés | 24 | Identique |
| Couverture Finale | 87% | Identique |
| **Tokens Utilisés** | **18,450** | **-60% vs v1.1** |
| **Tokens Moyens/Itération** | **1,537** | **-60% vs v1.1** |
| **Compressions Contexte** | **3** | **NOUVEAU** |
| **Événements Récupération** | **1** | **NOUVEAU** |
```

## Comparaison de Performance

| Version | Tokens/Itération | Temps de Chargement | Usage Mémoire |
|---------|-----------------|-------------------|--------------|
| **v1.1 (monolithique)** | ~3,850 | 100% | 100% |
| **v2.0 (modulaire)** | ~1,537 | 60% plus rapide | 50% inférieur |

## Architecture

**Composants Modulaires :**
- `ralph-loop-core.yaml` - Logique essentielle du loop
- `ralph-loop-prompts.yaml` - Templates optimisés en tokens  
- `ralph-loop-completion.yaml` - Détection intelligente
- `ralph-loop-recovery.yaml` | Récupération tokens & reprise
- `ralph-loop.yaml` | Orchestrateur principal avec chargement paresseux
