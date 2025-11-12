"""
Application Streamlit pour visualiser l'optimisation par colonies de fourmis en temps réel.
Version avec intégration des benchmarks et support multi-cœur parallèle.
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch
import time
import sys
import os
from multiprocessing import cpu_count

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

    # Afficher le nombre de cœurs disponibles
    n_cores = cpu_count()
    st.info(f"🖥️ Cette machine dispose de **{n_cores} cœurs CPU** disponibles pour le calcul parallèle.")

    # Boutons pour gérer les benchmarks
    col1, col2, col3 = st.columns(3)

    with col1:
        quick_mode = st.checkbox("Mode rapide (tests légers)", value=False, key="bench_quick_mode")
        parallel_mode = st.checkbox(f"🚀 Mode parallèle ({n_cores} cœurs)", value=False, key="bench_parallel_mode")

        if parallel_mode:
            st.caption(f"⚡ Accélération estimée: {n_cores}x plus rapide!")

    with col2:
        if st.button("🚀 Lancer les benchmarks", type="primary", key="bench_button_run"):
            mode_str = "parallèle" if parallel_mode else "séquentiel"
            with st.spinner(f"Exécution des benchmarks en mode {mode_str}... Cela peut prendre plusieurs minutes."):
                # Utiliser un container pour afficher les logs
                log_placeholder = st.empty()

                # Exécuter les benchmarks
                df_results = run_default_benchmarks(
                    quick_mode=quick_mode,
                    parallel=parallel_mode
                )

                # Sauvegarder les résultats
                save_benchmarks(df_results, "exports/benchmarks.csv")

                success_msg = f"✅ Benchmarks terminés! {len(df_results)} configurations testées."
                if parallel_mode:
                    success_msg += f"\n⚡ Mode parallèle utilisé sur {n_cores} cœurs."

                st.success(success_msg)
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
        st.markdown("#### 📊 Analyses Scientifiques par Série")

        st.info("📊 **Approche scientifique** : Chaque série teste l'impact d'UN SEUL paramètre en gardant les autres constants.")

        # Créer des onglets pour les 9 séries scientifiques
        graph_tabs = st.tabs([
            "1️⃣ Nombre de villes",
            "2️⃣ Nombre de fourmis",
            "3️⃣ Nombre de cycles",
            "4️⃣ Alpha (phéromones)",
            "5️⃣ Beta (visibilité)",
            "6️⃣ Persistance p",
            "7️⃣ Ratio m/n",
            "8️⃣ Reproductibilité",
            "9️⃣ Configs extrêmes"
        ])

        # ========== SÉRIE 1 : NOMBRE DE VILLES ==========
        with graph_tabs[0]:
            st.markdown("### 📊 Série 1 : Impact du Nombre de Villes")
            st.markdown("**Question** : Comment le temps et la qualité évoluent-ils avec la taille du problème ?")
            st.markdown("**Variables fixes** : m=n (ratio 1:1), cycles=300, seed=42")

            # Filtrer les données de la série 1 : m=n et cycles=300
            df_serie1 = df[(df['m'] == df['n']) & (df['cycles'] == 300) & (df['seed'] == 42)]

            if len(df_serie1) > 0:
                # Trier par n et supprimer les doublons (garder la dernière occurrence)
                df_serie1 = df_serie1.sort_values('n').drop_duplicates(subset=['n'], keep='last').reset_index(drop=True)

                fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(14, 6))

                # Graphique 1a : Temps vs Nombre de villes
                ax1a.plot(df_serie1['n'], df_serie1['runtime_sec'], 'o-',
                         color='blue', linewidth=2, markersize=8)
                ax1a.set_xlabel('Nombre de villes (n)', fontsize=12)
                ax1a.set_ylabel('Temps d\'exécution (secondes)', fontsize=12)
                ax1a.set_title('⏱️ Scalabilité : Temps vs Taille', fontsize=13, weight='bold')
                ax1a.grid(True, alpha=0.3)

                # Graphique 1b : Qualité vs Nombre de villes
                ax1b.plot(df_serie1['n'], df_serie1['best_len_global'], 'o-',
                         color='green', linewidth=2, markersize=8)
                ax1b.set_xlabel('Nombre de villes (n)', fontsize=12)
                ax1b.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax1b.set_title('🎯 Qualité de la solution', fontsize=13, weight='bold')
                ax1b.grid(True, alpha=0.3)

                plt.tight_layout()
                st.pyplot(fig1)
                plt.close(fig1)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie1) > 1:
                    ratio_temps = df_serie1['runtime_sec'].iloc[-1] / df_serie1['runtime_sec'].iloc[0]
                    ratio_villes = df_serie1['n'].iloc[-1] / df_serie1['n'].iloc[0]
                    st.write(f"- Ratio temps (n={df_serie1['n'].iloc[-1]}/{df_serie1['n'].iloc[0]}): **{ratio_temps:.1f}x** plus long")
                    st.write(f"- Complexité observée: O(n^{np.log(ratio_temps)/np.log(ratio_villes):.2f})")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 2 : NOMBRE DE FOURMIS ==========
        with graph_tabs[1]:
            st.markdown("### 📊 Série 2 : Impact du Nombre de Fourmis")
            st.markdown("**Question** : Plus de fourmis = meilleure solution ? À quel coût ?")
            st.markdown("**Variables fixes** : n=300, cycles=300, seed=42")

            # Filtrer : n=300, cycles=300
            df_serie2 = df[(df['n'] == 300) & (df['cycles'] == 300) & (df['seed'] == 42)]

            if len(df_serie2) > 0:
                # Trier par m et supprimer les doublons
                df_serie2 = df_serie2.sort_values('m').drop_duplicates(subset=['m'], keep='last').reset_index(drop=True)

                fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 6))

                # Graphique 2a : Temps vs Fourmis
                ax2a.plot(df_serie2['m'], df_serie2['runtime_sec'], 'o-',
                         color='blue', linewidth=2, markersize=8)
                ax2a.set_xlabel('Nombre de fourmis (m)', fontsize=12)
                ax2a.set_ylabel('Temps d\'exécution (secondes)', fontsize=12)
                ax2a.set_title('⏱️ Coût du nombre de fourmis', fontsize=13, weight='bold')
                ax2a.grid(True, alpha=0.3)

                # Graphique 2b : Qualité vs Fourmis (rendements décroissants)
                ax2b.plot(df_serie2['m'], df_serie2['best_len_global'], 'o-',
                         color='green', linewidth=2, markersize=8)
                ax2b.set_xlabel('Nombre de fourmis (m)', fontsize=12)
                ax2b.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax2b.set_title('🎯 Rendements décroissants ?', fontsize=13, weight='bold')
                ax2b.grid(True, alpha=0.3)

                plt.tight_layout()
                st.pyplot(fig2)
                plt.close(fig2)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie2) > 3:
                    # Trouver le point d'inflexion (amélioration < 1%)
                    improvements = []
                    for i in range(1, len(df_serie2)):
                        prev_qual = df_serie2['best_len_global'].iloc[i-1]
                        curr_qual = df_serie2['best_len_global'].iloc[i]
                        improv = ((prev_qual - curr_qual) / prev_qual) * 100
                        improvements.append(improv)

                    st.write(f"- Temps double tous les ~{df_serie2['m'].iloc[len(df_serie2)//2] / df_serie2['m'].iloc[0]:.0f}x fourmis")
                    st.write(f"- Amélioration moyenne par doublement: {np.mean(improvements):.2f}%")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 3 : NOMBRE DE CYCLES ==========
        with graph_tabs[2]:
            st.markdown("### 📊 Série 3 : Impact du Nombre de Cycles")
            st.markdown("**Question** : Combien de cycles pour converger ? Plateau ?")
            st.markdown("**Variables fixes** : n=200, m=200, seed=42")

            # Filtrer : n=200, m=200
            df_serie3 = df[(df['n'] == 200) & (df['m'] == 200) & (df['seed'] == 42)]

            if len(df_serie3) > 0:
                # Trier par cycles et supprimer les doublons
                df_serie3 = df_serie3.sort_values('cycles').drop_duplicates(subset=['cycles'], keep='last').reset_index(drop=True)

                fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6))

                # Graphique 3a : Convergence
                ax3a.plot(df_serie3['cycles'], df_serie3['best_len_global'], 'o-',
                         color='darkgreen', linewidth=2, markersize=8)
                ax3a.set_xlabel('Nombre de cycles', fontsize=12)
                ax3a.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax3a.set_title('📉 Courbe de convergence', fontsize=13, weight='bold')
                ax3a.grid(True, alpha=0.3)

                # Graphique 3b : Amélioration par cycle
                if len(df_serie3) > 1:
                    improvements_pct = []
                    for i in range(1, len(df_serie3)):
                        improv = ((df_serie3['best_len_global'].iloc[0] - df_serie3['best_len_global'].iloc[i]) /
                                 df_serie3['best_len_global'].iloc[0]) * 100
                        improvements_pct.append(improv)

                    ax3b.plot(df_serie3['cycles'].iloc[1:], improvements_pct, 'o-',
                             color='orange', linewidth=2, markersize=8)
                    ax3b.set_xlabel('Nombre de cycles', fontsize=12)
                    ax3b.set_ylabel('Amélioration totale (%)', fontsize=12)
                    ax3b.set_title('📈 Amélioration cumulée', fontsize=13, weight='bold')
                    ax3b.grid(True, alpha=0.3)

                plt.tight_layout()
                st.pyplot(fig3)
                plt.close(fig3)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie3) > 2:
                    best_50 = df_serie3[df_serie3['cycles'] <= 100]['best_len_global'].min()
                    best_all = df_serie3['best_len_global'].min()
                    gain = ((best_50 - best_all) / best_50) * 100
                    st.write(f"- Amélioration après 100 cycles: déjà {100-gain:.1f}% de la solution finale")
                    st.write(f"- Cycles recommandés: 200-300 (bon compromis temps/qualité)")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 4 : PARAMÈTRE ALPHA ==========
        with graph_tabs[3]:
            st.markdown("### 📊 Série 4 : Impact du Paramètre Alpha")
            st.markdown("**Question** : Quelle importance des phéromones ?")
            st.markdown("**Variables fixes** : n=100, m=100, cycles=300, beta=5.0, seed=42")

            # Filtrer : n=100, m=100, cycles=300, beta=5.0
            df_serie4 = df[(df['n'] == 100) & (df['m'] == 100) & (df['cycles'] == 300) &
                          (df['beta'] == 5.0) & (df['seed'] == 42)]

            if len(df_serie4) > 0:
                # Trier par alpha et supprimer les doublons
                df_serie4 = df_serie4.sort_values('alpha').drop_duplicates(subset=['alpha'], keep='last').reset_index(drop=True)

                fig4, ax4 = plt.subplots(figsize=(12, 6))

                ax4.plot(df_serie4['alpha'], df_serie4['best_len_global'], 'o-',
                        color='purple', linewidth=3, markersize=10)
                ax4.set_xlabel('Alpha (influence phéromones)', fontsize=12)
                ax4.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax4.set_title('🧪 Influence des phéromones sur la qualité', fontsize=14, weight='bold')
                ax4.axvline(x=1.0, color='red', linestyle='--', alpha=0.5, label='Alpha standard (1.0)')
                ax4.grid(True, alpha=0.3)
                ax4.legend()

                plt.tight_layout()
                st.pyplot(fig4)
                plt.close(fig4)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie4) > 2:
                    best_alpha = df_serie4.loc[df_serie4['best_len_global'].idxmin(), 'alpha']
                    st.write(f"- **Alpha optimal observé : {best_alpha:.1f}**")
                    st.write(f"- Alpha faible (< 1.0) : peu d'exploitation, plus d'exploration")
                    st.write(f"- Alpha élevé (> 2.0) : risque de convergence prématurée")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 5 : PARAMÈTRE BETA ==========
        with graph_tabs[4]:
            st.markdown("### 📊 Série 5 : Impact du Paramètre Beta")
            st.markdown("**Question** : Quelle importance de la visibilité (distance) ?")
            st.markdown("**Variables fixes** : n=100, m=100, cycles=300, alpha=1.0, seed=42")

            # Filtrer : n=100, m=100, cycles=300, alpha=1.0
            df_serie5 = df[(df['n'] == 100) & (df['m'] == 100) & (df['cycles'] == 300) &
                          (df['alpha'] == 1.0) & (df['seed'] == 42)]

            if len(df_serie5) > 0:
                # Trier par beta et supprimer les doublons
                df_serie5 = df_serie5.sort_values('beta').drop_duplicates(subset=['beta'], keep='last').reset_index(drop=True)

                fig5, ax5 = plt.subplots(figsize=(12, 6))

                ax5.plot(df_serie5['beta'], df_serie5['best_len_global'], 'o-',
                        color='darkred', linewidth=3, markersize=10)
                ax5.set_xlabel('Beta (influence visibilité)', fontsize=12)
                ax5.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax5.set_title('🔍 Influence de la visibilité sur la qualité', fontsize=14, weight='bold')
                ax5.axvline(x=5.0, color='red', linestyle='--', alpha=0.5, label='Beta standard (5.0)')
                ax5.grid(True, alpha=0.3)
                ax5.legend()

                plt.tight_layout()
                st.pyplot(fig5)
                plt.close(fig5)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie5) > 2:
                    best_beta = df_serie5.loc[df_serie5['best_len_global'].idxmin(), 'beta']
                    st.write(f"- **Beta optimal observé : {best_beta:.1f}**")
                    st.write(f"- Beta faible (< 3.0) : moins glouton, plus d'exploration")
                    st.write(f"- Beta élevé (> 7.0) : très glouton, exploitation locale")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 6 : PERSISTANCE p ==========
        with graph_tabs[5]:
            st.markdown("### 📊 Série 6 : Impact de la Persistance p")
            st.markdown("**Question** : Quel taux d'évaporation optimal ?")
            st.markdown("**Variables fixes** : n=100, m=100, cycles=300, seed=42")
            st.markdown("**Note** : p = 1 - taux_évaporation (p élevé = peu d'évaporation)")

            # Filtrer : n=100, m=100, cycles=300 (et alpha/beta par défaut)
            df_serie6 = df[(df['n'] == 100) & (df['m'] == 100) & (df['cycles'] == 300) & (df['seed'] == 42)]
            # Exclure les variations d'alpha et beta
            df_serie6 = df_serie6[(df_serie6['alpha'] == 1.0) & (df_serie6['beta'] == 5.0)]

            if len(df_serie6) > 0:
                # Trier par p et supprimer les doublons
                df_serie6 = df_serie6.sort_values('p').drop_duplicates(subset=['p'], keep='last').reset_index(drop=True)

                fig6, ax6 = plt.subplots(figsize=(12, 6))

                ax6.plot(df_serie6['p'], df_serie6['best_len_global'], 'o-',
                        color='teal', linewidth=3, markersize=10)
                ax6.set_xlabel('Persistance p (1 - évaporation)', fontsize=12)
                ax6.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax6.set_title('💨 Influence de l\'évaporation sur la qualité', fontsize=14, weight='bold')
                ax6.axvline(x=0.5, color='red', linestyle='--', alpha=0.5, label='p standard (0.5)')
                ax6.grid(True, alpha=0.3)
                ax6.legend()

                plt.tight_layout()
                st.pyplot(fig6)
                plt.close(fig6)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie6) > 2:
                    best_p = df_serie6.loc[df_serie6['best_len_global'].idxmin(), 'p']
                    st.write(f"- **p optimal observé : {best_p:.2f}**")
                    st.write(f"- p faible (< 0.4) : évaporation forte, oubli rapide")
                    st.write(f"- p élevé (> 0.7) : mémoire longue, risque de stagnation")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 7 : RATIO M/N ==========
        with graph_tabs[6]:
            st.markdown("### 📊 Série 7 : Impact du Ratio Fourmis/Villes")
            st.markdown("**Question** : Quel ratio m/n optimal ?")
            st.markdown("**Variables fixes** : n=200, cycles=300, seed=42")

            # Filtrer : n=200, cycles=300
            df_serie7 = df[(df['n'] == 200) & (df['cycles'] == 300) & (df['seed'] == 42)]

            if len(df_serie7) > 0:
                df_serie7['ratio_m_n'] = df_serie7['m'] / df_serie7['n']
                # Trier par ratio et supprimer les doublons
                df_serie7 = df_serie7.sort_values('ratio_m_n').drop_duplicates(subset=['ratio_m_n'], keep='last').reset_index(drop=True)

                fig7, (ax7a, ax7b) = plt.subplots(1, 2, figsize=(14, 6))

                # Graphique 7a : Qualité vs Ratio
                ax7a.plot(df_serie7['ratio_m_n'], df_serie7['best_len_global'], 'o-',
                         color='darkblue', linewidth=2, markersize=8)
                ax7a.set_xlabel('Ratio m/n', fontsize=12)
                ax7a.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                ax7a.set_title('🎯 Qualité vs Ratio', fontsize=13, weight='bold')
                ax7a.axvline(x=1.0, color='red', linestyle='--', alpha=0.5, label='Ratio 1:1')
                ax7a.grid(True, alpha=0.3)
                ax7a.legend()

                # Graphique 7b : Temps vs Ratio
                ax7b.plot(df_serie7['ratio_m_n'], df_serie7['runtime_sec'], 'o-',
                         color='orange', linewidth=2, markersize=8)
                ax7b.set_xlabel('Ratio m/n', fontsize=12)
                ax7b.set_ylabel('Temps d\'exécution (s)', fontsize=12)
                ax7b.set_title('⏱️ Coût vs Ratio', fontsize=13, weight='bold')
                ax7b.grid(True, alpha=0.3)

                plt.tight_layout()
                st.pyplot(fig7)
                plt.close(fig7)

                # Analyse
                st.markdown("**📈 Analyse :**")
                if len(df_serie7) > 2:
                    best_ratio = df_serie7.loc[df_serie7['best_len_global'].idxmin(), 'ratio_m_n']
                    st.write(f"- **Ratio optimal observé : {best_ratio:.2f}**")
                    st.write(f"- Ratio < 1.0 : peu de fourmis, exploration limitée")
                    st.write(f"- Ratio ≈ 1.0 : équilibre classique (recommandé)")
                    st.write(f"- Ratio > 2.0 : beaucoup de fourmis, rendements décroissants")
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 8 : REPRODUCTIBILITÉ ==========
        with graph_tabs[7]:
            st.markdown("### 📊 Série 8 : Tests de Reproductibilité")
            st.markdown("**Question** : Résultats stables ? Quelle variance ?")
            st.markdown("**Variables fixes** : cycles=300")
            st.markdown("**Variable testée** : seed (5 seeds différents sur 5 tailles)")

            # Filtrer : cycles=300, grouper par taille
            df_serie8 = df[df['cycles'] == 300]

            if len(df_serie8) > 10:
                # Calculer variance par taille de problème
                variance_by_size = []
                sizes = [30, 50, 100, 200, 300]

                fig8, ax8 = plt.subplots(figsize=(12, 6))

                for size in sizes:
                    df_size = df_serie8[(df_serie8['n'] == size) & (df_serie8['m'] == size)]
                    if len(df_size) > 1:
                        variance_by_size.append({
                            'size': size,
                            'mean': df_size['best_len_global'].mean(),
                            'std': df_size['best_len_global'].std(),
                            'min': df_size['best_len_global'].min(),
                            'max': df_size['best_len_global'].max()
                        })

                if variance_by_size:
                    df_var = pd.DataFrame(variance_by_size)

                    # Box plot pour chaque taille
                    positions = []
                    data_to_plot = []
                    labels = []

                    for size in sizes:
                        df_size = df_serie8[(df_serie8['n'] == size) & (df_serie8['m'] == size)]
                        if len(df_size) > 1:
                            data_to_plot.append(df_size['best_len_global'].values)
                            positions.append(size)
                            labels.append(f'{size}')

                    if data_to_plot:
                        bp = ax8.boxplot(data_to_plot, positions=positions, widths=20,
                                        patch_artist=True, showmeans=True)

                        for patch in bp['boxes']:
                            patch.set_facecolor('lightblue')

                        ax8.set_xlabel('Taille du problème (n=m)', fontsize=12)
                        ax8.set_ylabel('Meilleure longueur trouvée', fontsize=12)
                        ax8.set_title('📊 Distribution et variance par taille', fontsize=14, weight='bold')
                        ax8.grid(True, alpha=0.3, axis='y')

                        plt.tight_layout()
                        st.pyplot(fig8)
                        plt.close(fig8)

                        # Analyse
                        st.markdown("**📈 Analyse :**")
                        st.write(f"- Variance faible : algorithme **stable** ✅")
                        st.write(f"- Variance élevée : résultats **dépendants du seed**")

                        # Tableau de variance
                        st.dataframe(df_var, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible pour cette série. Lancez les benchmarks complets.")

        # ========== SÉRIE 9 : CONFIGURATIONS EXTRÊMES ==========
        with graph_tabs[8]:
            st.markdown("### 📊 Série 9 : Configurations Extrêmes (Stress Test)")
            st.markdown("**Question** : Limites du système ?")

            # Les configs extrêmes sont difficiles à filtrer automatiquement
            # On va afficher les 10 configurations les plus longues
            df_serie9 = df.nlargest(10, 'runtime_sec')

            if len(df_serie9) > 0:
                fig9, ax9 = plt.subplots(figsize=(12, 6))

                labels = [f"{row['n']}v×{row['m']}f×{row['cycles']}c"
                         for _, row in df_serie9.iterrows()]

                colors = ['red' if x > 1000 else 'orange' if x > 500 else 'yellow'
                         for x in df_serie9['runtime_sec']]

                ax9.barh(range(len(df_serie9)), df_serie9['runtime_sec'], color=colors)
                ax9.set_yticks(range(len(df_serie9)))
                ax9.set_yticklabels(labels, fontsize=10)
                ax9.set_xlabel('Temps d\'exécution (secondes)', fontsize=12)
                ax9.set_title('🔥 Top 10 configurations les plus exigeantes', fontsize=14, weight='bold')
                ax9.grid(True, alpha=0.3, axis='x')

                plt.tight_layout()
                st.pyplot(fig9)
                plt.close(fig9)

                # Analyse
                st.markdown("**📈 Analyse :**")
                st.write(f"- Configuration la plus lourde : **{df_serie9.iloc[0]['runtime_sec']:.0f}s** ({df_serie9.iloc[0]['runtime_sec']/60:.1f} min)")
                st.write(f"- Plus grosse config : {int(df_serie9.iloc[0]['n'])} villes × {int(df_serie9.iloc[0]['m'])} fourmis × {int(df_serie9.iloc[0]['cycles'])} cycles")
                st.write(f"- Mémoire estimée : ~{(df_serie9.iloc[0]['n']**2 * 8 / 1024**2):.1f} MB")

                # Tableau des configs extrêmes
                st.markdown("**📋 Détails des configurations extrêmes :**")
                df_display = df_serie9[['n', 'm', 'cycles', 'runtime_sec', 'best_len_global']].copy()
                df_display['runtime_sec'] = df_display['runtime_sec'].round(1)
                df_display['best_len_global'] = df_display['best_len_global'].round(2)
                st.dataframe(df_display, use_container_width=True)
            else:
                st.warning("Aucune donnée disponible. Lancez les benchmarks complets.")

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

