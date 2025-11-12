"""
Module pour l'algorithme ACO (Ant Colony Optimization) appliqué au TSP.
"""
import numpy as np


class ANT:
    """
    Classe pour l'algorithme d'optimisation par colonies de fourmis (ANT).

    Cette classe initialise toutes les structures de données nécessaires pour
    l'algorithme ACO, sans encore simuler le mouvement des fourmis.
    """

    def __init__(self, coords, alpha=1.0, beta=5.0, p=0.5, Q=100.0, m=None, seed=None):
        """
        Args:
            coords (np.ndarray): Tableau de forme (n, 2) avec les coordonnées des villes
            alpha (float): Paramètre d'influence des phéromones (défaut: 1.0)
            beta (float): Paramètre d'influence de la visibilité (défaut: 5.0)
            p (float): Taux d'évaporation des phéromones, dans [0, 1] (défaut: 0.5)
            Q (float): Constante pour le dépôt de phéromones (défaut: 100.0)
            m (int, optional): Nombre de fourmis. Si None, utilise le nombre de villes
            seed (int, optional): Graine pour le générateur aléatoire
        """
        # Coordonnées des villes
        self.coords = np.array(coords)
        self.n = len(self.coords)

        # Hyperparamètres
        self.alpha = alpha  # Influence des phéromones
        self.beta = beta    # Influence de la visibilité
        self.p = p          # Taux d'évaporation
        self.Q = Q          # Constante de dépôt
        self.m = m if m is not None else self.n  # Nombre de fourmis

        # Générateur aléatoire
        self.rng = np.random.default_rng(seed)

        # Calcul de la matrice des distances
        self.dist = self._compute_distance_matrix()

        # Calcul de la visibilité (eta[i,j] = 1 / dist[i,j])
        self.eta = self._compute_visibility()

        # Initialisation de la matrice des phéromones (tau)
        self.tau = self._initialize_pheromones()

        # Meilleure solution trouvée
        self.best_tour = None
        self.best_len = float('inf')

    def _compute_distance_matrix(self):
        """
        Calcule la matrice des distances euclidiennes entre toutes les villes.
        Optimisé avec NumPy vectorisé (broadcasting).

        Returns:
            np.ndarray: Matrice (n, n) des distances
        """
        # Utiliser le broadcasting NumPy pour vectoriser le calcul
        diff = self.coords[:, np.newaxis, :] - self.coords[np.newaxis, :, :]
        dist = np.sqrt(np.sum(diff**2, axis=2))
        return dist

    def _compute_visibility(self):
        """
        Calcule la matrice de visibilité (inverse de la distance).
        eta[i,j] = 1 / dist[i,j] si i != j, sinon 0.
        Optimisé avec NumPy vectorisé.

        Returns:
            np.ndarray: Matrice (n, n) de visibilité
        """
        # Éviter la division par zéro avec np.divide et où
        with np.errstate(divide='ignore', invalid='ignore'):
            eta = np.divide(1.0, self.dist, where=self.dist > 0, out=np.zeros_like(self.dist))
        return eta

    def _initialize_pheromones(self):
        """
        Initialise la matrice des phéromones à 1.0 partout sauf sur la diagonale (0).

        Returns:
            np.ndarray: Matrice (n, n) de phéromones
        """
        tau = np.ones((self.n, self.n))
        np.fill_diagonal(tau, 0.0)

        return tau

    def get_info(self):
        """
        Retourne un dictionnaire avec les informations sur l'état actuel de l'ANT.

        Returns:
            dict: Informations sur les matrices et paramètres
        """
        return {
            'n_cities': self.n,
            'n_ants': self.m,
            'alpha': self.alpha,
            'beta': self.beta,
            'evaporation_rate': self.p,
            'Q': self.Q,
            'tau_shape': self.tau.shape,
            'eta_shape': self.eta.shape,
            'dist_shape': self.dist.shape,
            'best_length': self.best_len,
            'best_tour': self.best_tour
        }

    def build_random_tour(self, start_city):
        """
        Construit un tour aléatoire valide en visitant chaque ville exactement une fois.

        Cette méthode crée un tour simple sans utiliser les phéromones ou la visibilité,
        juste un ordre aléatoire des villes restantes.

        Args:
            start_city (int): Indice de la ville de départ

        Returns:
            list: Tour complet sous forme de liste d'indices [start, ..., start]
                  La ville de départ apparaît au début et à la fin.
        """
        # Créer une liste de toutes les villes sauf la ville de départ
        remaining_cities = [i for i in range(self.n) if i != start_city]

        # Mélanger aléatoirement les villes restantes
        self.rng.shuffle(remaining_cities)

        # Construire le tour complet : départ → villes mélangées → retour au départ
        tour = [start_city] + remaining_cities + [start_city]

        return tour

    def build_probabilistic_tour(self, start_city):
        """
        Construit un tour probabiliste guidé par tau^alpha * eta^beta.

        Utilise une liste tabou pour éviter de revisiter les villes, et une sélection
        par roulette (cumsum + random) pour choisir la prochaine ville selon les scores.

        Args:
            start_city (int): Indice de la ville de départ

        Returns:
            list: Tour complet sous forme de liste d'indices [start, ..., start]
        """
        # Initialiser le tour avec la ville de départ
        tour = [start_city]

        # Liste tabou : villes déjà visitées
        visited = {start_city}

        # Position actuelle
        current_city = start_city

        # Construire le tour ville par ville
        while len(tour) < self.n:
            # Liste des villes non visitées
            unvisited = [city for city in range(self.n) if city not in visited]

            if not unvisited:
                break

            # Calculer les scores w_ij = tau[i,j]^alpha * eta[i,j]^beta
            scores = np.zeros(len(unvisited))
            for idx, city in enumerate(unvisited):
                tau_value = self.tau[current_city, city]
                eta_value = self.eta[current_city, city]
                scores[idx] = (tau_value ** self.alpha) * (eta_value ** self.beta)

            # Normaliser les scores pour obtenir des probabilités
            total_score = scores.sum()

            if total_score == 0:
                # Si tous les scores sont nuls, choisir uniformément
                probabilities = np.ones(len(unvisited)) / len(unvisited)
            else:
                probabilities = scores / total_score

            # Sélection par roulette : cumsum + random
            cumulative_probs = np.cumsum(probabilities)
            random_value = self.rng.random()

            # Trouver l'index de la ville sélectionnée
            selected_idx = np.searchsorted(cumulative_probs, random_value)

            # S'assurer que l'index est valide (cas limite où random_value = 1.0)
            if selected_idx >= len(unvisited):
                selected_idx = len(unvisited) - 1

            # Ajouter la ville sélectionnée au tour
            next_city = unvisited[selected_idx]
            tour.append(next_city)
            visited.add(next_city)
            current_city = next_city

        # Fermer le tour en revenant à la ville de départ
        tour.append(start_city)

        return tour

    def tour_length(self, tour):
        """
        Calcule la longueur totale d'un tour donné.

        Args:
            tour (list): Liste d'indices représentant le tour (doit commencer et finir
                        par la même ville)

        Returns:
            float: Longueur totale du tour (somme des distances entre villes consécutives)
        """
        total_length = 0.0

        # Parcourir le tour et additionner les distances entre villes consécutives
        for i in range(len(tour) - 1):
            city_from = tour[i]
            city_to = tour[i + 1]
            total_length += self.dist[city_from, city_to]

        return total_length

    def __repr__(self):
        """Représentation en chaîne de caractères de l'objet ANT."""
        return (f"ANT(n_cities={self.n}, n_ants={self.m}, "
                f"alpha={self.alpha}, beta={self.beta}, p={self.p}, Q={self.Q})")

