"""
Module pour la vue console de l'application TSP avec ACO.
"""
import numpy as np
import time
from contextlib import contextmanager


@contextmanager
def time_block(label: str):
    """Context manager simple pour mesurer et afficher le temps d'une étape."""
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"[TIMER] {label}: {end - start:.6f} s")


class ConsoleView:
    """
    Classe pour gérer l'affichage des informations dans la console.
    """

    def __init__(self):
        """Initialise la vue console."""
        np.set_printoptions(precision=2, suppress=True, linewidth=120)

    def display_cities(self, cities):
        """
        Affiche les coordonnées des villes.

        Args:
            cities (np.ndarray): Tableau de coordonnées des villes
        """
        print("Coordonnées des villes :")
        print("-" * 40)
        for i, (x, y) in enumerate(cities):
            print(f"Ville {i:2d}: ({x:6.2f}, {y:6.2f})")

    def display_ant_info(self, ant):
        """
        Affiche les informations sur l'instance ANT.

        Args:
            ant: Instance de la classe ANT
        """
        print("\n" + "=" * 40)
        print("Initialisation de l'algorithme ANT :")
        print("-" * 40)
        print(ant)

        print("\n" + "=" * 40)
        print("Informations ANT :")
        print("-" * 40)
        info = ant.get_info()
        for key, value in info.items():
            print(f"{key:20s}: {value}")

    def display_matrix(self, matrix, title):
        """
        Affiche une matrice avec un titre.

        Args:
            matrix (np.ndarray): Matrice à afficher
            title (str): Titre de la matrice
        """
        print("\n" + "=" * 40)
        print(f"{title} :")
        print("-" * 40)
        print(matrix)

    def display_distance_stats(self, dist_matrix):
        """
        Affiche les statistiques sur les distances.

        Args:
            dist_matrix (np.ndarray): Matrice des distances
        """
        print("\n" + "=" * 40)
        print("Statistiques sur les distances :")
        print("-" * 40)
        non_zero_distances = dist_matrix[dist_matrix > 0]
        print(f"Distance minimale : {non_zero_distances.min():.2f}")
        print(f"Distance maximale : {non_zero_distances.max():.2f}")
        print(f"Distance moyenne  : {non_zero_distances.mean():.2f}")

    def display_tour(self, tour, length, start_city):
        """
        Affiche un tour et sa longueur.

        Args:
            tour (list): Liste d'indices du tour
            length (float): Longueur du tour
            start_city (int): Ville de départ
        """
        print(f"\nVille de départ : {start_city}")
        print(f"Tour généré     : {tour}")
        print(f"Longueur totale : {length:.2f}")

    def display_probabilistic_tour(self, tour, length, seed):
        """
        Affiche un tour probabiliste avec sa longueur et le seed utilisé.

        Args:
            tour (list): Liste d'indices du tour
            length (float): Longueur du tour
            seed (int): Graine aléatoire utilisée pour la reproductibilité
        """
        print(f"\nTour probabiliste (seed={seed}):")
        print(f"  Tour    : {tour}")
        print(f"  Longueur: {length:.2f}")

    def display_validation_results(self, validation_results):
        """
        Affiche les résultats de validation d'un tour.

        Args:
            validation_results (dict): Résultats de la validation
        """
        print("\n" + "-" * 40)
        print("Vérification du tour :")
        print("-" * 40)
        for message in validation_results['messages']:
            print(message)

    def display_multiple_tours(self, tours_and_lengths):
        """
        Affiche plusieurs tours avec comparaison.

        Args:
            tours_and_lengths (list): Liste de tuples (tour, longueur)
        """
        for i, (tour, length) in enumerate(tours_and_lengths, 1):
            print(f"\nTour {i}: {tour}")
            print(f"Longueur: {length:.2f}")

        if len(tours_and_lengths) > 1:
            best_tour, best_length = min(tours_and_lengths, key=lambda x: x[1])
            worst_tour, worst_length = max(tours_and_lengths, key=lambda x: x[1])

            print("\n" + "-" * 40)
            print(f"Meilleur tour (longueur: {best_length:.2f}):")
            print(f"  {best_tour}")
            print(f"Pire tour (longueur: {worst_length:.2f}):")
            print(f"  {worst_tour}")
            
            if best_length > 0:
                diff_percent = ((worst_length / best_length - 1) * 100)
                print(f"Différence: {worst_length - best_length:.2f} ({diff_percent:.1f}%)")

    def display_section_header(self, title):
        """
        Affiche un en-tête de section.

        Args:
            title (str): Titre de la section
        """
        print("\n" + "=" * 40)
        print(title)
        print("=" * 40)

    def display_message(self, message):
        """
        Affiche un message simple.

        Args:
            message (str): Message à afficher
        """
        print(message)

    def display_cycle_stats(self, cycle_index, stats_cycle):
        """
        Affiche les statistiques d'un cycle ACO.

        Args:
            cycle_index (int): Numéro du cycle
            stats_cycle (dict): Dictionnaire avec les statistiques du cycle
        """
        print("\n" + "=" * 60)
        print(f"Cycle {cycle_index} - Statistiques")
        print("=" * 60)

        print(f"Meilleure longueur du cycle : {stats_cycle['best_len_cycle']:.2f}")
        print(f"Longueur moyenne du cycle   : {stats_cycle['mean_len_cycle']:.2f}")
        print(f"Meilleure longueur globale  : {stats_cycle['best_len_global']:.2f}")

        if stats_cycle['best_tour_global']:
            print(f"Meilleur tour global        : {stats_cycle['best_tour_global']}")

        # Afficher les temps d'exécution de chaque étape
        print("\n" + "-" * 60)
        print("Temps d'exécution des étapes :")
        print("-" * 60)
        print(f"  Construction des tours : {stats_cycle['time_construction']:.6f} s")
        print(f"  Évaporation           : {stats_cycle['time_evaporation']:.6f} s")
        print(f"  Dépôt de phéromones   : {stats_cycle['time_deposit']:.6f} s")
        total_time = (stats_cycle['time_construction'] +
                     stats_cycle['time_evaporation'] +
                     stats_cycle['time_deposit'])
        print(f"  Total du cycle        : {total_time:.6f} s")

        # Afficher quelques statistiques sur les longueurs
        all_lengths = stats_cycle['all_lengths']
        print("\n" + "-" * 60)
        print(f"Statistiques sur les {len(all_lengths)} tours du cycle :")
        print("-" * 60)
        print(f"  Minimum  : {min(all_lengths):.2f}")
        print(f"  Maximum  : {max(all_lengths):.2f}")
        print(f"  Moyenne  : {np.mean(all_lengths):.2f}")
        print(f"  Écart-type : {np.std(all_lengths):.2f}")

    def display_convergence_summary(self, history):
        """
        Affiche un résumé de la convergence sur tous les cycles.

        Args:
            history (list): Liste des dictionnaires de statistiques de chaque cycle
        """
        print("\n" + "=" * 60)
        print("RÉSUMÉ DE CONVERGENCE")
        print("=" * 60)

        if not history:
            print("Aucun cycle exécuté.")
            return

        # Extraire les données
        best_len_per_cycle = [stats['best_len_cycle'] for stats in history]
        mean_len_per_cycle = [stats['mean_len_cycle'] for stats in history]
        best_len_global_per_cycle = [stats['best_len_global'] for stats in history]

        # Afficher l'évolution de la meilleure solution
        print("\nÉvolution de la meilleure solution globale :")
        print("-" * 60)
        for i, (best_cycle, best_global) in enumerate(zip(best_len_per_cycle, best_len_global_per_cycle), 1):
            improvement = ""
            if i > 1 and best_global < best_len_global_per_cycle[i-2]:
                improvement = " ← AMÉLIORATION!"
            print(f"  Cycle {i:2d}: Meilleur du cycle = {best_cycle:7.2f}, Meilleur global = {best_global:7.2f}{improvement}")

        # Statistiques globales
        print("\n" + "-" * 60)
        print("Statistiques globales :")
        print("-" * 60)
        print(f"  Meilleure solution trouvée : {min(best_len_global_per_cycle):.2f}")
        print(f"  Pire solution trouvée      : {max(best_len_per_cycle):.2f}")
        print(f"  Longueur moyenne (tous)    : {np.mean(best_len_per_cycle):.2f}")

        # Solution finale
        final_stats = history[-1]
        print("\n" + "-" * 60)
        print("Solution finale (meilleure globale) :")
        print("-" * 60)
        print(f"  Longueur : {final_stats['best_len_global']:.2f}")
        print(f"  Tour     : {final_stats['best_tour_global']}")

        # Temps total
        total_time_construction = sum(stats['time_construction'] for stats in history)
        total_time_evaporation = sum(stats['time_evaporation'] for stats in history)
        total_time_deposit = sum(stats['time_deposit'] for stats in history)
        total_time_all = total_time_construction + total_time_evaporation + total_time_deposit

        print("\n" + "-" * 60)
        print("Temps d'exécution total :")
        print("-" * 60)
        print(f"  Construction des tours : {total_time_construction:.6f} s")
        print(f"  Évaporation           : {total_time_evaporation:.6f} s")
        print(f"  Dépôt de phéromones   : {total_time_deposit:.6f} s")
        print(f"  TOTAL                 : {total_time_all:.6f} s")
        print(f"  Temps moyen par cycle : {total_time_all / len(history):.6f} s")
