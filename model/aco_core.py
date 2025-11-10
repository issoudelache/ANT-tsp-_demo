"""
Module pour le moteur ACO (Ant Colony Optimization) avec cycles complets.
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

        Returns:
            np.ndarray: Matrice (n, n) des distances
        """
        n = self.n
        dist = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    dx = self.coords[j, 0] - self.coords[i, 0]
                    dy = self.coords[j, 1] - self.coords[i, 1]
                    dist[i, j] = np.sqrt(dx**2 + dy**2)

        return dist

    def _compute_visibility(self):
        """
        Calcule la matrice de visibilité (inverse de la distance).
        eta[i,j] = 1 / dist[i,j] si i != j, sinon 0.

        Returns:
            np.ndarray: Matrice (n, n) de visibilité
        """
        eta = np.zeros((self.n, self.n))

        for i in range(self.n):
            for j in range(self.n):
                if i != j and self.dist[i, j] > 0:
                    eta[i, j] = 1.0 / self.dist[i, j]

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

    def _build_probabilistic_tour(self, start_city):
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

    def _tour_length(self, tour):
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

        # 1. Construction des tours par toutes les fourmis
        tours = []
        lengths = []

        for k in range(self.m):
            # Chaque fourmi part d'une ville différente (cyclique)
            start_city = k % self.n

            # Construire le tour probabiliste
            tour = self._build_probabilistic_tour(start_city)

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

        # 3. Dépôt de phéromones (Ant-Cycle)
        time_start_deposit = time.perf_counter()

        for k in range(self.m):
            tour = tours[k]
            L_k = lengths[k]

            # Dépôt sur chaque arête du tour
            for i in range(len(tour) - 1):
                city_from = tour[i]
                city_to = tour[i + 1]

                # Dépôt bidirectionnel (graphe non orienté)
                delta_tau = self.Q / L_k
                self.tau[city_from, city_to] += delta_tau
                self.tau[city_to, city_from] += delta_tau

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
