"""
Module pour la gestion du problème TSP (Traveling Salesman Problem).
"""
import numpy as np


def generate_cities(n, seed=None):
    """
    Génère n villes aléatoires en 2D dans l'espace [0, 100] × [0, 100].

    Args:
        n (int): Nombre de villes à générer
        seed (int, optional): Graine pour la reproductibilité

    Returns:
        np.ndarray: Tableau de forme (n, 2) contenant les coordonnées (x, y) des villes
    """
    rng = np.random.default_rng(seed)
    cities = rng.uniform(0, 100, size=(n, 2))
    return cities


def compute_distance_matrix(coords):
    """
    Calcule la matrice des distances euclidiennes entre toutes les villes.
    Optimisé avec NumPy vectorisé (broadcasting).

    Args:
        coords (np.ndarray): Tableau de forme (n, 2) avec les coordonnées des villes

    Returns:
        np.ndarray: Matrice (n, n) où dist[i, j] = distance euclidienne entre ville i et j
    """
    # Utiliser le broadcasting NumPy pour vectoriser le calcul
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    dist = np.sqrt(np.sum(diff**2, axis=2))
    return dist


def tour_length(tour, dist_matrix):
    """
    Calcule la longueur totale d'un tour donné.

    Args:
        tour (list): Liste d'indices représentant le tour (doit commencer et finir
                    par la même ville)
        dist_matrix (np.ndarray): Matrice des distances entre villes

    Returns:
        float: Longueur totale du tour (somme des distances entre villes consécutives)
    """
    total_length = 0.0

    for i in range(len(tour) - 1):
        city_from = tour[i]
        city_to = tour[i + 1]
        total_length += dist_matrix[city_from, city_to]

    return total_length


def validate_tour(tour, n_cities):
    """
    Vérifie qu'un tour est valide pour le TSP.

    Args:
        tour (list): Liste d'indices représentant le tour
        n_cities (int): Nombre total de villes

    Returns:
        dict: Dictionnaire avec les résultats de validation
    """
    results = {
        'valid': True,
        'messages': []
    }

    # Vérifier que le tour commence et finit par la même ville
    if tour[0] != tour[-1]:
        results['valid'] = False
        results['messages'].append(f"✗ Le tour commence à {tour[0]} mais finit à {tour[-1]}")
    else:
        results['messages'].append(f"✓ Le tour commence et finit à la ville {tour[0]}")

    # Vérifier que toutes les villes sont visitées exactement une fois (sauf retour)
    tour_without_return = tour[:-1]
    unique_cities = set(tour_without_return)

    if len(unique_cities) == n_cities:
        results['messages'].append(f"✓ Toutes les {n_cities} villes sont visitées exactement une fois")
    else:
        results['valid'] = False
        results['messages'].append(f"✗ {len(unique_cities)} villes uniques au lieu de {n_cities}")

    # Vérifier qu'il n'y a pas de doublons (sauf le retour)
    if len(tour_without_return) == len(unique_cities):
        results['messages'].append(f"✓ Aucune ville n'est visitée deux fois (sauf le retour)")
    else:
        results['valid'] = False
        results['messages'].append(f"✗ Des villes sont visitées plusieurs fois")

    # Vérifier que toutes les villes de 0 à n-1 sont présentes
    expected_cities = set(range(n_cities))
    if unique_cities == expected_cities:
        results['messages'].append(f"✓ Toutes les villes de 0 à {n_cities-1} sont présentes")
    else:
        results['valid'] = False
        missing = expected_cities - unique_cities
        extra = unique_cities - expected_cities
        if missing:
            results['messages'].append(f"✗ Villes manquantes : {missing}")
        if extra:
            results['messages'].append(f"✗ Villes en trop : {extra}")

    return results

