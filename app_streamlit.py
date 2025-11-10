"""
Application Streamlit pour visualiser l'optimisation par colonies de fourmis en temps réel.
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
import time
import sys
import os

# Ajouter le répertoire courant au chemin pour permettre les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.tsp_model import generate_cities
from model.aco_core import ACOEngine


def plot_tour(cities, tour, title="Chemin actuel", color='blue', length=None):
    """
    Crée un graphique matplotlib montrant le tour des villes.

    Args:
        cities (np.ndarray): Coordonnées des villes (n, 2)
        tour (list): Liste d'indices représentant le tour
        title (str): Titre du graphique
        color (str): Couleur du chemin
        length (float): Longueur du tour à afficher

    Returns:
        matplotlib.figure.Figure: Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Tracer les villes
    ax.scatter(cities[:, 0], cities[:, 1], c='red', s=200, zorder=3,
               edgecolors='black', linewidths=2, label='Villes')

    # Annoter les villes avec leurs numéros
    for i, (x, y) in enumerate(cities):
        ax.annotate(str(i), (x, y), fontsize=10, ha='center', va='center',
                   color='white', weight='bold')

    # Tracer le tour si fourni
    if tour and len(tour) > 1:
        for i in range(len(tour) - 1):
            city_from = tour[i]
            city_to = tour[i + 1]

            x_from, y_from = cities[city_from]
            x_to, y_to = cities[city_to]

            # Tracer la ligne
            ax.plot([x_from, x_to], [y_from, y_to],
                   color=color, linewidth=2.5, alpha=0.7, zorder=1)

            # Ajouter une flèche pour montrer la direction au début
            if i == 0:
                arrow = FancyArrowPatch(
                    (x_from, y_from), (x_to, y_to),
                    arrowstyle='->', mutation_scale=25,
                    linewidth=2.5, color=color, alpha=0.9, zorder=2
                )
                ax.add_patch(arrow)

    ax.set_xlabel('X', fontsize=14)
    ax.set_ylabel('Y', fontsize=14)

    # Ajouter la longueur au titre si fournie
    if length is not None:
        title = f"{title}\nLongueur: {length:.2f}"

    ax.set_title(title, fontsize=16, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')

    # Ajouter une marge autour des points
    margin = 5
    ax.set_xlim(cities[:, 0].min() - margin, cities[:, 0].max() + margin)
    ax.set_ylim(cities[:, 1].min() - margin, cities[:, 1].max() + margin)

    plt.tight_layout()
    return fig


def plot_convergence(history):
    """
    Crée un graphique de convergence montrant l'évolution des longueurs.

    Args:
        history (list): Liste des statistiques de chaque cycle

    Returns:
        matplotlib.figure.Figure: Figure matplotlib
    """
    if not history:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    cycles = list(range(1, len(history) + 1))
    best_len_cycle = [stats['best_len_cycle'] for stats in history]
    mean_len_cycle = [stats['mean_len_cycle'] for stats in history]
    best_len_global = [stats['best_len_global'] for stats in history]

    ax.plot(cycles, best_len_cycle, 'o-', label='Meilleur du cycle',
           color='green', linewidth=2, markersize=6, alpha=0.7)
    ax.plot(cycles, mean_len_cycle, 's-', label='Moyenne du cycle',
           color='orange', linewidth=2, markersize=6, alpha=0.7)
    ax.plot(cycles, best_len_global, 'D-', label='Meilleur global',
           color='red', linewidth=3, markersize=8)

    ax.set_xlabel('Cycle', fontsize=14)
    ax.set_ylabel('Longueur du tour', fontsize=14)
    ax.set_title('Convergence de l\'algorithme ACO', fontsize=16, weight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_pheromone_heatmap(tau, title="Matrice des phéromones"):
    """
    Crée une heatmap de la matrice des phéromones.

    Args:
        tau (np.ndarray): Matrice des phéromones
        title (str): Titre du graphique

    Returns:
        matplotlib.figure.Figure: Figure matplotlib
    """
    fig, ax = plt.subplots(figsize=(8, 7))

    im = ax.imshow(tau, cmap='YlOrRd', interpolation='nearest')
    ax.set_title(title, fontsize=16, weight='bold')
    ax.set_xlabel('Ville de destination', fontsize=12)
    ax.set_ylabel('Ville de départ', fontsize=12)

    # Ajouter une barre de couleur
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Niveau de phéromone', fontsize=12)

    plt.tight_layout()
    return fig


def main():
    """
    Application principale Streamlit.
    """
    # Configuration de la page
    st.set_page_config(
        page_title="ACO - Optimisation par Colonies de Fourmis",
        page_icon="🐜",
        layout="wide"
    )

    # Titre principal
    st.title("🐜 Optimisation par Colonies de Fourmis (ACO)")
    st.markdown("### Visualisation en temps réel du problème du voyageur de commerce (TSP)")

    # Barre latérale pour les paramètres
    st.sidebar.header("⚙️ Paramètres")

    # Paramètres du problème
    st.sidebar.subheader("Problème TSP")
    n_cities = st.sidebar.slider("Nombre de villes", min_value=5, max_value=50, value=15, step=1)
    seed = st.sidebar.number_input("Graine aléatoire (seed)", min_value=0, max_value=10000, value=42, step=1)

    # Paramètres ACO
    st.sidebar.subheader("Paramètres ACO")
    n_ants = st.sidebar.slider("Nombre de fourmis", min_value=5, max_value=100, value=n_cities, step=5)
    alpha = st.sidebar.slider("Alpha (influence phéromones)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    beta = st.sidebar.slider("Beta (influence visibilité)", min_value=0.1, max_value=10.0, value=5.0, step=0.5)
    rho = st.sidebar.slider("Rho (taux d'évaporation)", min_value=0.1, max_value=0.9, value=0.5, step=0.05)
    Q = st.sidebar.slider("Q (constante de dépôt)", min_value=10.0, max_value=500.0, value=100.0, step=10.0)

    # Paramètres d'exécution
    st.sidebar.subheader("Exécution")
    n_cycles = st.sidebar.slider("Nombre de cycles", min_value=1, max_value=200, value=50, step=5)
    update_interval = st.sidebar.slider("Mise à jour tous les X cycles", min_value=1, max_value=20, value=1, step=1)

    # Bouton pour lancer l'optimisation
    if st.sidebar.button("🚀 Lancer l'optimisation", type="primary"):
        # Réinitialiser l'état
        if 'running' not in st.session_state:
            st.session_state.running = True

        # Générer les villes
        with st.spinner("Génération des villes..."):
            cities = generate_cities(n_cities, seed=int(seed))

        st.success(f"✅ {n_cities} villes générées avec succès!")

        # Initialiser le moteur ACO
        with st.spinner("Initialisation du moteur ACO..."):
            engine = ACOEngine(
                coords=cities,
                alpha=alpha,
                beta=beta,
                p=rho,  # p est le facteur de persistance (1 - taux d'évaporation)
                Q=Q,
                m=n_ants,
                seed=int(seed)
            )

        # Créer les placeholders pour l'affichage en temps réel
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📍 Meilleur chemin trouvé")
            tour_placeholder = st.empty()

        with col2:
            st.subheader("📊 Statistiques")
            stats_placeholder = st.empty()

        # Graphique de convergence
        st.subheader("📈 Convergence de l'algorithme")
        convergence_placeholder = st.empty()

        # Barre de progression
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Historique
        history = []

        # Exécution des cycles
        for cycle_idx in range(1, n_cycles + 1):
            # Exécuter un cycle
            stats_cycle = engine.run_cycle()
            history.append(stats_cycle)

            # Mettre à jour la barre de progression
            progress = cycle_idx / n_cycles
            progress_bar.progress(progress)
            status_text.text(f"Cycle {cycle_idx}/{n_cycles} - Meilleure longueur: {stats_cycle['best_len_global']:.2f}")

            # Mettre à jour l'affichage tous les X cycles ou au dernier cycle
            if cycle_idx % update_interval == 0 or cycle_idx == n_cycles:
                # Afficher le meilleur tour
                with tour_placeholder.container():
                    fig_tour = plot_tour(
                        cities,
                        stats_cycle['best_tour_global'],
                        title=f"Meilleur chemin global (Cycle {cycle_idx})",
                        color='darkblue',
                        length=stats_cycle['best_len_global']
                    )
                    st.pyplot(fig_tour)
                    plt.close(fig_tour)

                # Afficher les statistiques
                with stats_placeholder.container():
                    st.metric(
                        label="🏆 Meilleur du cycle",
                        value=f"{stats_cycle['best_len_cycle']:.2f}"
                    )
                    st.metric(
                        label="📊 Moyenne du cycle",
                        value=f"{stats_cycle['mean_len_cycle']:.2f}"
                    )
                    st.metric(
                        label="⭐ Meilleur global",
                        value=f"{stats_cycle['best_len_global']:.2f}"
                    )

                    # Statistiques supplémentaires
                    st.markdown("---")
                    st.markdown("**Détails du cycle:**")
                    st.write(f"- Min: {min(stats_cycle['all_lengths']):.2f}")
                    st.write(f"- Max: {max(stats_cycle['all_lengths']):.2f}")
                    st.write(f"- Écart-type: {np.std(stats_cycle['all_lengths']):.2f}")

                # Afficher le graphique de convergence
                with convergence_placeholder.container():
                    fig_conv = plot_convergence(history)
                    if fig_conv:
                        st.pyplot(fig_conv)
                        plt.close(fig_conv)

                # Petit délai pour voir l'animation
                time.sleep(0.05)

        # Affichage final
        progress_bar.progress(1.0)
        status_text.text(f"✅ Optimisation terminée! Meilleure longueur: {history[-1]['best_len_global']:.2f}")

        # Résumé final
        st.success("🎉 Optimisation terminée avec succès!")

        # Afficher les résultats finaux dans des onglets
        tab1, tab2, tab3 = st.tabs(["📍 Meilleur chemin", "🔥 Phéromones", "📋 Résumé"])

        with tab1:
            st.subheader("Meilleur chemin trouvé")
            final_stats = history[-1]
            fig_final = plot_tour(
                cities,
                final_stats['best_tour_global'],
                title="Solution finale",
                color='darkgreen',
                length=final_stats['best_len_global']
            )
            st.pyplot(fig_final)
            plt.close(fig_final)

            # Afficher le tour
            with st.expander("🗺️ Voir le tour complet"):
                st.code(str(final_stats['best_tour_global']))

        with tab2:
            st.subheader("Matrice des phéromones finale")
            fig_phero = plot_pheromone_heatmap(engine.tau)
            st.pyplot(fig_phero)
            plt.close(fig_phero)

            st.info("Les zones plus claires indiquent des niveaux de phéromones plus élevés, "
                   "représentant les chemins les plus empruntés par les fourmis.")

        with tab3:
            st.subheader("Résumé de l'optimisation")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="Meilleure solution",
                    value=f"{min([s['best_len_global'] for s in history]):.2f}"
                )

            with col2:
                st.metric(
                    label="Solution initiale",
                    value=f"{history[0]['best_len_cycle']:.2f}"
                )

            with col3:
                improvement = ((history[0]['best_len_cycle'] - history[-1]['best_len_global']) /
                              history[0]['best_len_cycle'] * 100)
                st.metric(
                    label="Amélioration",
                    value=f"{improvement:.1f}%"
                )

            # Tableau récapitulatif
            st.markdown("#### 📊 Évolution par cycle")

            # Créer un dataframe pour affichage
            import pandas as pd
            df_data = {
                'Cycle': list(range(1, len(history) + 1)),
                'Meilleur du cycle': [s['best_len_cycle'] for s in history],
                'Moyenne du cycle': [s['mean_len_cycle'] for s in history],
                'Meilleur global': [s['best_len_global'] for s in history]
            }
            df = pd.DataFrame(df_data)

            # Afficher les 10 premiers et 10 derniers cycles
            st.write("**Premiers cycles:**")
            st.dataframe(df.head(10), use_container_width=True)

            if len(history) > 20:
                st.write("**Derniers cycles:**")
                st.dataframe(df.tail(10), use_container_width=True)

    else:
        # Affichage initial avant le lancement
        st.info("👈 Configurez les paramètres dans la barre latérale et cliquez sur **Lancer l'optimisation**")

        # Afficher un exemple de visualisation
        st.markdown("---")
        st.subheader("À propos de l'algorithme ACO")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **L'optimisation par colonies de fourmis (ACO)** est un algorithme inspiré du comportement 
            des fourmis réelles qui trouvent le chemin le plus court vers la nourriture.
            
            **Principe:**
            1. Les fourmis construisent des solutions de manière probabiliste
            2. Elles déposent des phéromones sur leur chemin
            3. Les meilleures solutions accumulent plus de phéromones
            4. Les fourmis suivent préférentiellement les chemins avec plus de phéromones
            """)

        with col2:
            st.markdown("""
            **Paramètres clés:**
            - **Alpha (α)**: Influence des phéromones dans le choix du chemin
            - **Beta (β)**: Influence de la distance (visibilité) dans le choix
            - **Rho (ρ)**: Taux d'évaporation des phéromones
            - **Q**: Quantité de phéromones déposées par les fourmis
            - **m**: Nombre de fourmis dans la colonie
            """)


if __name__ == "__main__":
    main()

