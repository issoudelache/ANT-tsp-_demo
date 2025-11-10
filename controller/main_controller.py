"""
Module contrôleur principal pour l'application TSP avec ACO.
"""
import sys
import os

# Ajouter le répertoire parent au chemin pour permettre les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.tsp_model import generate_cities
from model.aco_core import ACOEngine
from view.console_view import ConsoleView, time_block


class MainController:
    """
    Contrôleur principal qui coordonne le modèle et la vue.
    """

    def __init__(self, n_cities=20, seed=42, n_cycles=1000):
        """
        Initialise le contrôleur.

        Args:
            n_cities (int): Nombre de villes à générer
            seed (int): Graine aléatoire pour la reproductibilité
            n_cycles (int): Nombre de cycles ACO à exécuter
        """
        self.n_cities = n_cities
        self.seed = seed
        self.n_cycles = n_cycles
        self.view = ConsoleView()
        self.cities = None
        self.engine = None
        self.history = []  # Historique de convergence

    def run(self):
        """
        Lance l'application complète avec plusieurs cycles ACO.
        """
        # Génération des villes
        with time_block("Génération des villes"):
            self.view.display_message(f"Génération de {self.n_cities} villes aléatoires...\n")
            self.cities = generate_cities(self.n_cities, seed=self.seed)

        # Affichage des coordonnées
        with time_block("Affichage des coordonnées"):
            self.view.display_cities(self.cities)

        # Initialisation du moteur ACO
        with time_block("Initialisation du moteur ACO"):
            self.engine = ACOEngine(
                coords=self.cities,
                alpha=1,
                beta=5,
                p=0.5,
                Q=100,
                m=self.n_cities,
                seed=self.seed
            )
            self.view.display_message(f"\n{self.engine}")

        # Exécution de plusieurs cycles ACO
        self.view.display_section_header(f"Exécution de {self.n_cycles} cycles ACO")

        with time_block(f"Exécution des {self.n_cycles} cycles"):
            # Intervalle d'affichage de progression (tous les 10% des cycles ou minimum 100)
            progress_interval = max(self.n_cycles // 10, 100)

            for cycle_idx in range(1, self.n_cycles + 1):
                # Exécuter un cycle
                stats_cycle = self.engine.run_cycle()

                # Sauvegarder dans l'historique
                self.history.append(stats_cycle)

                # Afficher la progression périodiquement
                if cycle_idx % progress_interval == 0 or cycle_idx == self.n_cycles:
                    best_global = self.engine.best_len_global
                    self.view.display_message(
                        f"  Cycle {cycle_idx}/{self.n_cycles} - "
                        f"Meilleure longueur globale: {best_global:.2f}"
                    )

        # Afficher un résumé de la convergence
        with time_block("Affichage du résumé de convergence"):
            self.view.display_convergence_summary(self.history)


def main():
    """
    Point d'entrée principal de l'application.
    """
    controller = MainController(n_cities=100, seed=43, n_cycles=1000)
    controller.run()


if __name__ == "__main__":
    main()

