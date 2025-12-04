"""
Vérifier et afficher les résultats d'entraînement du modèle
"""

import os
import json
from pathlib import Path

def check_training_results():
    """Vérifie les résultats d'entraînement"""
    
    print("\n" + "="*60)
    print("VÉRIFICATION DES RÉSULTATS D'ENTRAÎNEMENT")
    print("="*60)
    
    # Vérifier le modèle
    model_path = "models/yolov8n-seg_trained.pt"
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024*1024)
        print(f"✓ Modèle entraîné: {model_path} ({size:.1f} MB)")
    else:
        print(f"✗ Modèle NON trouvé: {model_path}")
        return False
    
    # Vérifier les logs d'entraînement
    train_logs = Path("runs/segment").glob("*/results.csv")
    train_logs = list(train_logs)
    
    if train_logs:
        print(f"✓ Logs d'entraînement trouvés: {len(train_logs)} fichier(s)")
        
        # Afficher les derniers résultats
        latest_log = train_logs[-1]
        try:
            import pandas as pd
            df = pd.read_csv(latest_log)
            print(f"\n📊 Dernières métriques:")
            print(f"   Nombre d'époques: {len(df)}")
            last_row = df.iloc[-1]
            print(f"   Dernière perte: {last_row.get('train/box_loss', 'N/A')}")
        except:
            print("   (Impossible de lire les détails)")
    else:
        print("⚠ Logs d'entraînement NON trouvés")
    
    # Vérifier le dossier de poids
    weights_dir = Path("runs/segment").glob("*/weights")
    if list(weights_dir):
        print(f"✓ Dossier des poids d'entraînement trouvé")
    
    print("="*60 + "\n")
    return True

if __name__ == '__main__':
    check_training_results()
