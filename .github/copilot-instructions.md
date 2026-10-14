# Consignes du projet

## Architecture

- `src/` contient les algorithmes et structures métier. Garder la logique de calcul indépendante de l’interface.
- `src/dijkstra.py` est la référence classique ; `src/dynamic_algo.py` maintient les plus courts chemins par mises à jour incrémentales (`DynamicDijkstra`).
- `ui/` contient l’application CustomTkinter, organisée par responsabilités : orchestration (`app.py`), contrôles, dessin du graphe, panneaux, disposition, traces, constantes et modèles.
- `app.py` à la racine est le point d’entrée compatible. Préserver son exécution avec `python -m app` et `python app.py`.
- Les tests sont dans `tests/`. Le `README.md` décrit les commandes et la structure du dépôt.

## Conventions de modification

- Modifier le module propriétaire du comportement ; éviter de déplacer la logique métier dans l’interface.
- Préserver les API publiques et le comportement existant, sauf demande explicite.
- Pour l’algorithme dynamique, vérifier les ajouts, changements de poids et suppressions d’arêtes ; comparer les distances à Dijkstra classique.
- Les modifications de graphe de l’interface doivent mettre à jour l’algorithme dynamique, le calcul classique, la comparaison et les traces.
- Chaque module Python doit importer explicitement tous les noms qu’il utilise. Après extraction ou déplacement de code, contrôler particulièrement les imports des callbacks CustomTkinter, qui peuvent ne s’exécuter qu’à l’interaction.

## Vérification

- Lancer les tests avec `pytest` (ou `.venv/bin/pytest -q` si l’environnement virtuel du projet est disponible).
- Ajouter ou lancer un test ciblé pour tout comportement modifié ; pour l’algorithme dynamique, couvrir la comparaison avec Dijkstra classique après les modifications d’arêtes.
- Pour les changements de l’interface, vérifier au minimum l’import de `app` et, lorsque l’environnement graphique est disponible, lancer avec `python -m app` et tester les interactions concernées.
- Exécuter `git diff --check` avant de conclure.
