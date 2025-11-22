"""
Script de configuration et setup du projet
"""

import subprocess
import sys
from pathlib import Path
import os

PROJECT_DIR = Path(__file__).parent

def check_python_version():
    """Vérifier la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]}")

def install_dependencies():
    """Installer les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    requirements_file = PROJECT_DIR / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ {requirements_file} non trouvé")
        return False
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
            env={**os.environ, "PIP_NO_CACHE_DIR": "1"}
        )
        print("✓ Dépendances installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠ Attention lors de l'installation (non bloquant): {e}")
        return True  # Continuer même si erreur

def create_directories():
    """Créer les répertoires nécessaires"""
    print("\n📁 Création des répertoires...")
    
    directories = [
        PROJECT_DIR / "models",
        PROJECT_DIR / "runs",
        PROJECT_DIR / "evaluations",
        PROJECT_DIR / "void_rate_results",
        PROJECT_DIR / "inferences",
    ]
    
    for dir_path in directories:
        dir_path.mkdir(exist_ok=True)
        print(f"  ✓ {dir_path.name}/")

def verify_dataset():
    """Vérifier le dataset"""
    print("\n📊 Vérification du dataset...")
    
    required_dirs = [
        PROJECT_DIR / "train" / "images",
        PROJECT_DIR / "train" / "labels",
        PROJECT_DIR / "valid" / "images",
        PROJECT_DIR / "valid" / "labels",
        PROJECT_DIR / "test" / "images",
        PROJECT_DIR / "test" / "labels",
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            print(f"  ✓ {dir_path.relative_to(PROJECT_DIR)}: {len(files)} fichiers")
        else:
            print(f"  ⚠ {dir_path.relative_to(PROJECT_DIR)}: NON TROUVÉ")

def verify_data_yaml():
    """Vérifier le fichier data.yaml"""
    print("\n📝 Vérification de data.yaml...")
    
    data_yaml = PROJECT_DIR / "data.yaml"
    if data_yaml.exists():
        print(f"  ✓ {data_yaml.name} trouvé")
    else:
        print(f"  ❌ {data_yaml.name} introuvable")

def main():
    """Fonction principale"""
    print("=" * 80)
    print("🚀 CONFIGURATION DU PROJET YOLOv11-SEGMENTATION")
    print("=" * 80)
    
    # Vérification
    check_python_version()
    verify_data_yaml()
    create_directories()
    verify_dataset()
    
    # Installation
    if not install_dependencies():
        print("\n⚠ Erreur lors de l'installation des dépendances")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURATION TERMINÉE")
    print("=" * 80)
    print("\n📚 Prochaines étapes:")
    print("  1. Entraîner le modèle: python train.py")
    print("  2. Évaluer le modèle: python evaluate.py")
    print("  3. Calculer void_rate: python void_rate_calculator.py")
    print("  4. Inférence: python inference.py")
    print("\n💡 Pour voir l'entraînement: tensorboard --logdir runs/")

if __name__ == "__main__":
    main()
