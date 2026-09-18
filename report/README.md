# Recherche sur les Algorithmes de Plus Court Chemin Dynamiques

## Introduction

Ce projet explore les algorithmes de plus court chemin dynamiques, capables de maintenir efficacement les chemins optimaux lors de modifications du graphe (ajout/suppression d'arêtes, modification de poids).

## État de l'Art

### Dijkstra Classique
- Complexité: O((V + E) log V) avec heap de Fibonacci
- Recalcul complet à chaque modification
- Baseline pour nos comparaisons

### Algorithmes Dynamiques
- **D* Lite**: Adapté pour la planification robotique
- **LPA* (Lifelong Planning A*)**: Réutilise les calculs précédents
- Approches incrémentales: mise à jour partielle du graphe

## Méthodologie

### Structure Expérimentale

1. **Génération de graphes de test**
   - Graphes aléatoires (densité variable)
   - Grilles (navigation)
   - Graphes épars (réseaux réels)

2. **Scénarios de modification**
   - Augmentation de poids d'arête
   - Diminution de poids d'arête
   - Suppression d'arête
   - Ajout d'arête
   - Ajout de nœud

3. **Métriques de performance**
   - Temps de recalcul
   - Speedup (algorithme dynamique vs recalcul complet)
   - Scalabilité (variation avec taille du graphe)

### Implémentation

- Langage: Python 3.8+
- Structure de données: graphe orienté pondéré dynamique
- Algorithmes: Dijkstra baseline + variante dynamique

## Résultats

*À compléter après exécution des benchmarks*

### Performance par Scénario

| Scénario | Temps Classique | Temps Dynamique | Speedup |
|----------|----------------|-----------------|---------|
| ...      | ...            | ...             | ...     |

### Analyse de Scalabilité

*Graphiques et analyse à ajouter*

## Discussion

### Points Clés

- Conditions favorables aux algorithmes dynamiques
- Impact du type de modification
- Trade-offs complexité/performance

### Limitations

- Hypothèses simplificatrices
- Scope des scénarios testés
- Comparaison avec autres algorithmes

### Travaux Futurs

- Extension aux graphes non-orientés
- Algorithmes parallèles
- Applications temps-réel

## Références

1. Koenig, S., & Likhachev, M. (2002). D* Lite. AAAI/IAAI.
2. Ramalingam, G., & Reps, T. (1996). An incremental algorithm for a generalization of the shortest-path problem.
3. Demetrescu, C., & Italiano, G. F. (2004). A new approach to dynamic all pairs shortest paths.

## Annexes

### Installation et Utilisation

```bash
# Installation
pip install -r requirements.txt

# Exécution des tests
pytest

# Exécution des benchmarks
python experiments/benchmark.py
```

### Structure du Code

Voir README.md principal du projet.
