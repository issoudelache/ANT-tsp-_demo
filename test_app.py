"""
Script de test pour vérifier que l'application fonctionne correctement.
"""
import sys
import os

# Ajouter le répertoire courant au chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.tsp_model import generate_cities
from model.aco_core import ACOEngine

print("=" * 60)
print("Test de l'application ACO")
print("=" * 60)

# Test 1: Génération des villes
print("\n1. Test de génération des villes...")
cities = generate_cities(10, seed=42)
print(f"   ✓ {len(cities)} villes générées avec succès")

# Test 2: Initialisation du moteur ACO
print("\n2. Test d'initialisation du moteur ACO...")
engine = ACOEngine(
    coords=cities,
    alpha=1.0,
    beta=5.0,
    p=0.5,
    Q=100.0,
    m=10,
    seed=42
)
print(f"   ✓ Moteur ACO initialisé: {engine}")

# Test 3: Exécution d'un cycle
print("\n3. Test d'exécution d'un cycle...")
stats = engine.run_cycle()
print(f"   ✓ Cycle exécuté avec succès")
print(f"   - Meilleur du cycle: {stats['best_len_cycle']:.2f}")
print(f"   - Moyenne du cycle: {stats['mean_len_cycle']:.2f}")
print(f"   - Meilleur global: {stats['best_len_global']:.2f}")

# Test 4: Exécution de plusieurs cycles
print("\n4. Test d'exécution de 5 cycles...")
for i in range(5):
    stats = engine.run_cycle()
print(f"   ✓ 5 cycles exécutés avec succès")
print(f"   - Meilleure solution finale: {stats['best_len_global']:.2f}")

print("\n" + "=" * 60)
print("✅ Tous les tests sont passés avec succès!")
print("=" * 60)
print("\nVous pouvez maintenant lancer l'application Streamlit:")
print("  > streamlit run app_streamlit.py")
print("\nOu double-cliquez sur 'lancer_app.bat'")

