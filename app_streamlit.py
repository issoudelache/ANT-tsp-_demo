"""
Application Streamlit pour visualiser l'optimisation par colonies de fourmis en temps réel.
Version avec intégration des benchmarks.
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch
import time
import sys
import os

# Ajouter le répertoire courant au chemin pour permettre les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.tsp_model import generate_cities
from model.aco_core import ACOEngine
from model.benchmark import load_benchmarks, save_benchmarks
from controller.benchmark_controller import run_default_benchmarks


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


def render_simulation_tab():
    """
    Affiche le contenu de l'onglet Simulation ACO.
    """
    st.sidebar.header("⚙️ Paramètres de Simulation")

    # Paramètres du problème
    st.sidebar.subheader("Problème TSP")
    n_cities = st.sidebar.slider("Nombre de villes", min_value=5, max_value=500, value=50, step=5, key="sim_n_cities")
    seed = st.sidebar.number_input("Graine aléatoire (seed)", min_value=0, max_value=10000, value=42, step=1, key="sim_seed")

    # Paramètres ACO
    st.sidebar.subheader("Paramètres ACO")
    n_ants = st.sidebar.slider("Nombre de fourmis", min_value=5, max_value=500, value=min(n_cities, 50), step=5, key="sim_n_ants")
    alpha = st.sidebar.slider("Alpha (influence phéromones)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="sim_alpha")
    beta = st.sidebar.slider("Beta (influence visibilité)", min_value=0.1, max_value=10.0, value=5.0, step=0.5, key="sim_beta")
    rho = st.sidebar.slider("Rho (taux d'évaporation)", min_value=0.1, max_value=0.9, value=0.5, step=0.05, key="sim_rho")
    Q = st.sidebar.slider("Q (constante de dépôt)", min_value=10.0, max_value=500.0, value=100.0, step=10.0, key="sim_Q")

    # Paramètres d'exécution
    st.sidebar.subheader("Exécution")
    n_cycles = st.sidebar.slider("Nombre de cycles", min_value=1, max_value=5000, value=100, step=10, key="sim_n_cycles")
    update_interval = st.sidebar.slider("Mise à jour tous les X cycles", min_value=1, max_value=100, value=10, step=5, key="sim_update_interval")

    # Bouton pour lancer l'optimisation
    if st.sidebar.button("🚀 Lancer l'optimisation", type="primary", key="sim_button_launch"):
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
                p=(1.0 - rho),  # p est le facteur de persistance = 1 - taux d'évaporation
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
                        stats_cycle['best_tour_global'].tolist() if hasattr(stats_cycle['best_tour_global'], 'tolist') else stats_cycle['best_tour_global'],
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

        # Afficher les résultats finaux dans des sous-onglets
        tab1, tab2, tab3 = st.tabs(["📍 Meilleur chemin", "🔥 Phéromones", "📋 Résumé"])

        with tab1:
            st.subheader("Meilleur chemin trouvé")
            final_stats = history[-1]
            best_tour = final_stats['best_tour_global'].tolist() if hasattr(final_stats['best_tour_global'], 'tolist') else final_stats['best_tour_global']
            fig_final = plot_tour(
                cities,
                best_tour,
                title="Solution finale",
                color='darkgreen',
                length=final_stats['best_len_global']
            )
            st.pyplot(fig_final)
            plt.close(fig_final)

            # Afficher le tour
            with st.expander("🗺️ Voir le tour complet"):
                st.code(str(best_tour))

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
            df_data = {
                'Cycle': list(range(1, len(history) + 1)),
                'Meilleur du cycle': [s['best_len_cycle'] for s in history],
                'Moyenne du cycle': [s['mean_len_cycle'] for s in history],
                'Meilleur global': [s['best_len_global'] for s in history]
            }
            df = pd.DataFrame(df_data)

            # Afficher les 10 premiers et 10 derniers cycles
            st.write("**Premiers cycles:**")
            st.dataframe(df.head(10), width='stretch')

            if len(history) > 20:
                st.write("**Derniers cycles:**")
                st.dataframe(df.tail(10), width='stretch')

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
            
            **Optimisations :**
            - ✅ Calculs vectorisés avec NumPy
            - ✅ Performance : jusqu'à 500 villes et 5000 cycles
            - ✅ Temps réel pour grandes instances
            """)


def render_benchmarks_tab():
    """
    Affiche le contenu de l'onglet Benchmarks / Comparaison.
    """
    st.header("📊 Benchmarks de Performance")
    st.markdown("Comparez les performances de l'algorithme ACO avec différentes configurations.")

    # Boutons pour gérer les benchmarks
    col1, col2, col3 = st.columns(3)

    with col1:
        quick_mode = st.checkbox("Mode rapide (tests légers)", value=False, key="bench_quick_mode")

    with col2:
        if st.button("🚀 Lancer les benchmarks", type="primary", key="bench_button_run"):
            with st.spinner("Exécution des benchmarks en cours... Cela peut prendre plusieurs minutes."):
                # Utiliser un container pour afficher les logs
                log_placeholder = st.empty()

                # Exécuter les benchmarks
                df_results = run_default_benchmarks(quick_mode=quick_mode)

                # Sauvegarder les résultats
                save_benchmarks(df_results, "exports/benchmarks.csv")

                st.success(f"✅ Benchmarks terminés! {len(df_results)} configurations testées.")
                st.balloons()

    with col3:
        if st.button("🔄 Recharger les données", key="bench_button_reload"):
            st.rerun()

    # Charger les benchmarks existants
    df = load_benchmarks("exports/benchmarks.csv")

    if df is not None and len(df) > 0:
        st.markdown("---")
        st.subheader("📈 Résultats des Benchmarks")

        # Afficher les statistiques générales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Nombre de tests", len(df))

        with col2:
            st.metric("Temps moyen", f"{df['runtime_sec'].mean():.2f}s")

        with col3:
            st.metric("Config la plus rapide", f"{df['runtime_sec'].min():.2f}s")

        with col4:
            st.metric("Config la plus lente", f"{df['runtime_sec'].max():.2f}s")

        # Tableau des résultats
        st.markdown("#### 📋 Tableau des résultats")

        # Formater le dataframe pour l'affichage
        df_display = df.copy()
        df_display['runtime_sec'] = df_display['runtime_sec'].round(2)
        df_display['time_per_cycle'] = df_display['time_per_cycle'].round(4)
        df_display['best_len_global'] = df_display['best_len_global'].round(2)
        df_display['improvement_pct'] = df_display['improvement_pct'].round(1)

        st.dataframe(df_display, width='stretch', height=300)

        # Graphiques de comparaison
        st.markdown("#### 📊 Graphiques de Comparaison")

        # Créer des onglets pour différents graphiques
        graph_tab1, graph_tab2, graph_tab3, graph_tab4 = st.tabs([
            "Temps d'exécution",
            "Qualité des solutions",
            "Impact du nombre de fourmis",
            "Impact du nombre de villes"
        ])

        with graph_tab1:
            st.subheader("Temps d'exécution par configuration")

            # Graphique en barres
            fig1, ax1 = plt.subplots(figsize=(12, 6))

            df_sorted = df.sort_values('runtime_sec')
            x_labels = [f"n={row['n']}, m={row['m']}, c={row['cycles']}"
                       for _, row in df_sorted.iterrows()]

            ax1.barh(range(len(df_sorted)), df_sorted['runtime_sec'], color='steelblue')
            ax1.set_yticks(range(len(df_sorted)))
            ax1.set_yticklabels(x_labels, fontsize=9)
            ax1.set_xlabel('Temps d\'exécution (secondes)', fontsize=12)
            ax1.set_title('Temps d\'exécution total par configuration', fontsize=14, weight='bold')
            ax1.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()
            st.pyplot(fig1)
            plt.close(fig1)

        with graph_tab2:
            st.subheader("Qualité des solutions trouvées")

            fig2, ax2 = plt.subplots(figsize=(12, 6))

            df_sorted = df.sort_values('best_len_global')
            x_labels = [f"n={row['n']}, m={row['m']}"
                       for _, row in df_sorted.iterrows()]

            ax2.barh(range(len(df_sorted)), df_sorted['best_len_global'], color='green', alpha=0.7)
            ax2.set_yticks(range(len(df_sorted)))
            ax2.set_yticklabels(x_labels, fontsize=9)
            ax2.set_xlabel('Meilleure longueur trouvée', fontsize=12)
            ax2.set_title('Qualité de la meilleure solution par configuration', fontsize=14, weight='bold')
            ax2.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

        with graph_tab3:
            st.subheader("Impact du nombre de fourmis sur les performances")

            # Grouper par nombre de fourmis
            df_by_ants = df.groupby('m').agg({
                'runtime_sec': 'mean',
                'best_len_global': 'mean',
                'improvement_pct': 'mean'
            }).reset_index()

            fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6))

            # Temps vs nombre de fourmis
            ax3a.plot(df_by_ants['m'], df_by_ants['runtime_sec'], 'o-',
                     color='blue', linewidth=2, markersize=8)
            ax3a.set_xlabel('Nombre de fourmis', fontsize=12)
            ax3a.set_ylabel('Temps moyen (s)', fontsize=12)
            ax3a.set_title('Temps d\'exécution vs Nombre de fourmis', fontsize=13, weight='bold')
            ax3a.grid(True, alpha=0.3)

            # Qualité vs nombre de fourmis
            ax3b.plot(df_by_ants['m'], df_by_ants['best_len_global'], 'o-',
                     color='green', linewidth=2, markersize=8)
            ax3b.set_xlabel('Nombre de fourmis', fontsize=12)
            ax3b.set_ylabel('Longueur moyenne', fontsize=12)
            ax3b.set_title('Qualité de solution vs Nombre de fourmis', fontsize=13, weight='bold')
            ax3b.grid(True, alpha=0.3)

            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

        with graph_tab4:
            st.subheader("Impact du nombre de villes sur les performances")

            # Grouper par nombre de villes
            df_by_cities = df.groupby('n').agg({
                'runtime_sec': 'mean',
                'best_len_global': 'mean',
                'time_per_cycle': 'mean'
            }).reset_index()

            fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 6))

            # Temps vs nombre de villes
            ax4a.plot(df_by_cities['n'], df_by_cities['runtime_sec'], 'o-',
                     color='red', linewidth=2, markersize=8)
            ax4a.set_xlabel('Nombre de villes', fontsize=12)
            ax4a.set_ylabel('Temps moyen (s)', fontsize=12)
            ax4a.set_title('Temps d\'exécution vs Nombre de villes', fontsize=13, weight='bold')
            ax4a.grid(True, alpha=0.3)

            # Temps par cycle vs nombre de villes
            ax4b.plot(df_by_cities['n'], df_by_cities['time_per_cycle'], 'o-',
                     color='purple', linewidth=2, markersize=8)
            ax4b.set_xlabel('Nombre de villes', fontsize=12)
            ax4b.set_ylabel('Temps par cycle (s)', fontsize=12)
            ax4b.set_title('Temps par cycle vs Nombre de villes', fontsize=13, weight='bold')
            ax4b.grid(True, alpha=0.3)

            plt.tight_layout()
            st.pyplot(fig4)
            plt.close(fig4)

        # Téléchargement des données
        st.markdown("---")
        st.markdown("#### 💾 Télécharger les données")

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les résultats (CSV)",
            data=csv,
            file_name="benchmarks_aco.csv",
            mime="text/csv",
            key="bench_download"
        )

    else:
        st.info("📭 Aucun résultat de benchmark disponible. Lancez les benchmarks pour commencer!")

        st.markdown("""
        ### À propos des Benchmarks
        
        Les benchmarks permettent de :
        - **Mesurer les performances** de l'algorithme sur cette machine
        - **Comparer différentes configurations** (nombre de villes, fourmis, cycles)
        - **Identifier les paramètres optimaux** pour votre cas d'usage
        - **Visualiser l'impact** de chaque paramètre sur le temps et la qualité
        
        **Configurations testées par défaut :**
        - Variation du nombre de villes (30 à 200)
        - Variation du nombre de fourmis (10 à 150)
        - Variation du nombre de cycles (50 à 200)
        
        Les résultats sont sauvegardés automatiquement dans `exports/benchmarks.csv`.
        """)


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
    st.markdown("⚡ **Version optimisée** avec NumPy vectorisé - Speedup ~25-30x")

    # Créer des onglets principaux
    tab_simulation, tab_benchmarks = st.tabs(["🔬 Simulation ACO", "📊 Benchmarks / Comparaison"])

    # Onglet Simulation
    with tab_simulation:
        render_simulation_tab()

    # Onglet Benchmarks
    with tab_benchmarks:
        render_benchmarks_tab()


if __name__ == "__main__":
    main()

