"""
Module pour le moteur ACO (Ant Colony Optimization) avec cycles complets.
Optimisé avec NumPy vectorisé pour des performances maximales.
"""
import numpy as np
import time


class ACOEngine:
    """
    Moteur d'optimisation par colonies de fourmis (ACO Engine).

    Cette classe orchestre les cycles complets de l'algorithme Ant System :
    - Construction de tours par plusieurs fourmis
    - Évaporation des phéromones
    - Dépôt de phéromones (Ant-Cycle)
    - Mise à jour du meilleur tour global
    """

    def __init__(self, coords, alpha=1.0, beta=5.0, p=0.5, Q=100.0, m=None, seed=None):
        """
        Initialise le moteur ACO.

        Args:
            coords (np.ndarray): Tableau de forme (n, 2) avec les coordonnées des villes
            alpha (float): Paramètre d'influence des phéromones (défaut: 1.0)
            beta (float): Paramètre d'influence de la visibilité (défaut: 5.0)
            p (float): Facteur de persistance des phéromones, dans [0, 1] (défaut: 0.5)
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
        self.p = p          # Facteur de persistance (1 - taux d'évaporation)
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

        # Meilleure solution globale trouvée
        self.best_tour_global = None
        self.best_len_global = float('inf')

    def _compute_distance_matrix(self):
        """
        Calcule la matrice des distances euclidiennes entre toutes les villes.
        Optimisé avec NumPy vectorisé (broadcasting).

        Returns:
            np.ndarray: Matrice (n, n) des distances
        """
        # Utiliser le broadcasting NumPy pour vectoriser le calcul
        # coords[:, np.newaxis] crée une forme (n, 1, 2)
        # coords[np.newaxis, :] crée une forme (1, n, 2)
        # La différence donne une forme (n, n, 2)
        diff = self.coords[:, np.newaxis, :] - self.coords[np.newaxis, :, :]
        # Calculer les distances euclidiennes
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

    def _build_probabilistic_tour(self, start_city, tau_alpha=None, eta_beta=None):
        """
        Construit un tour probabiliste guidé par tau^alpha * eta^beta.
        Optimisé avec des tableaux NumPy et des masques booléens.

        Args:
            start_city (int): Indice de la ville de départ
            tau_alpha (np.ndarray, optional): Matrice tau^alpha précalculée
            eta_beta (np.ndarray, optional): Matrice eta^beta précalculée

        Returns:
            np.ndarray: Tour complet sous forme de tableau d'indices [start, ..., start]
        """
        # Utiliser un tableau NumPy pour le tour
        tour = np.empty(self.n + 1, dtype=np.int32)
        tour[0] = start_city

        # Masque booléen pour les villes visitées (plus rapide qu'un set)
        visited = np.zeros(self.n, dtype=bool)
        visited[start_city] = True

        # Précalculer tau^alpha et eta^beta si non fournis
        if tau_alpha is None:
            tau_alpha = self.tau ** self.alpha
        if eta_beta is None:
            eta_beta = self.eta ** self.beta

        current_city = start_city

        # Construire le tour ville par ville
        for step in range(1, self.n):
            # Calculer les scores pour toutes les villes non visitées
            scores = tau_alpha[current_city] * eta_beta[current_city]

            # Masquer les villes déjà visitées
            scores[visited] = 0

            # Normaliser les scores
            total_score = scores.sum()

            if total_score > 0:
                probabilities = scores / total_score
                # Sélection par roulette avec searchsorted
                cumulative_probs = np.cumsum(probabilities)
                random_value = self.rng.random()
                next_city = np.searchsorted(cumulative_probs, random_value)

                # Correction pour le cas limite
                if next_city >= self.n:
                    next_city = self.n - 1
            else:
                # Choisir uniformément parmi les villes non visitées
                unvisited_indices = np.where(~visited)[0]
                next_city = self.rng.choice(unvisited_indices)

            tour[step] = next_city
            visited[next_city] = True
            current_city = next_city

        # Fermer le tour
        tour[self.n] = start_city

        return tour

    def _tour_length(self, tour):
        """
        Calcule la longueur totale d'un tour donné.

        Args:
            tour (np.ndarray): Tableau d'indices représentant le tour (doit commencer et finir
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

    def run_cycle(self):
        """
        Exécute un cycle complet de l'algorithme Ant System :
        1. Chaque fourmi construit un tour probabiliste
        2. Évaporation des phéromones
        3. Dépôt de phéromones (Ant-Cycle)
        4. Mise à jour du meilleur tour global

        Returns:
            dict: Statistiques du cycle avec :
                - best_len_cycle: meilleure longueur du cycle
                - mean_len_cycle: longueur moyenne du cycle
                - best_len_global: meilleure longueur globale historique
                - best_tour_global: meilleur tour global
                - all_lengths: liste de toutes les longueurs du cycle
                - time_construction: temps de construction des tours (secondes)
                - time_evaporation: temps d'évaporation (secondes)
                - time_deposit: temps de dépôt (secondes)
        """
        # Mesurer le temps de chaque étape
        time_start_construction = time.perf_counter()

        # Précalculer tau^alpha et eta^beta une seule fois pour toutes les fourmis
        tau_alpha = self.tau ** self.alpha
        eta_beta = self.eta ** self.beta

        # 1. Construction des tours par toutes les fourmis
        tours = []
        lengths = []

        for k in range(self.m):
            # Chaque fourmi part d'une ville différente (cyclique)
            start_city = k % self.n

            # Construire le tour probabiliste avec les matrices précalculées
            tour = self._build_probabilistic_tour(start_city, tau_alpha, eta_beta)

            # Calculer la longueur du tour
            length = self._tour_length(tour)

            tours.append(tour)
            lengths.append(length)

        time_end_construction = time.perf_counter()
        time_construction = time_end_construction - time_start_construction

        # 2. Évaporation des phéromones
        time_start_evaporation = time.perf_counter()

        self.tau *= self.p  # p est le facteur de persistance

        time_end_evaporation = time.perf_counter()
        time_evaporation = time_end_evaporation - time_start_evaporation

        # 3. Dépôt de phéromones (Ant-Cycle) - Optimisé avec vectorisation
        time_start_deposit = time.perf_counter()

        # Convertir les tours en tableau NumPy pour vectorisation
        tours_array = np.array(tours, dtype=np.int32)
        lengths_array = np.array(lengths, dtype=np.float64)

        # Calculer les deltas pour chaque fourmi
        deltas = self.Q / lengths_array

        # Déposer les phéromones pour toutes les fourmis
        for k in range(self.m):
            tour = tours_array[k]
            delta_tau = deltas[k]

            # Extraire les paires (ville_from, ville_to)
            cities_from = tour[:-1]
            cities_to = tour[1:]

            # Dépôt bidirectionnel vectorisé
            np.add.at(self.tau, (cities_from, cities_to), delta_tau)
            np.add.at(self.tau, (cities_to, cities_from), delta_tau)

        time_end_deposit = time.perf_counter()
        time_deposit = time_end_deposit - time_start_deposit

        # 4. Mise à jour du meilleur tour global
        best_len_cycle = min(lengths)
        best_idx_cycle = lengths.index(best_len_cycle)
        best_tour_cycle = tours[best_idx_cycle]

        if best_len_cycle < self.best_len_global:
            self.best_len_global = best_len_cycle
            self.best_tour_global = best_tour_cycle.copy()

        # Calculer la longueur moyenne du cycle
        mean_len_cycle = np.mean(lengths)

        # Retourner les statistiques du cycle
        stats_cycle = {
            'best_len_cycle': best_len_cycle,
            'mean_len_cycle': mean_len_cycle,
            'best_len_global': self.best_len_global,
            'best_tour_global': self.best_tour_global,
            'all_lengths': lengths,
            'time_construction': time_construction,
            'time_evaporation': time_evaporation,
            'time_deposit': time_deposit
        }

        return stats_cycle

    def __repr__(self):
        """Représentation en chaîne de caractères de l'objet ACOEngine."""
        return (f"ACOEngine(n_cities={self.n}, n_ants={self.m}, "
                f"alpha={self.alpha}, beta={self.beta}, p={self.p}, Q={self.Q})")

