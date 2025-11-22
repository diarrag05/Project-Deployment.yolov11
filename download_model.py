#!/usr/bin/env python
"""
Script pour télécharger les poids YOLOv11 pour segmentation
"""

from pathlib import Path
import sys
import urllib.request
import os

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ ultralytics non installé")
    print("Exécutez d'abord: pip install ultralytics")
    sys.exit(1)

print("=" * 80)
print("📥 Téléchargement des poids YOLOv11m pour segmentation...")
print("=" * 80)
print("\n⏳ Cela peut prendre 2-5 minutes (le modèle pèse ~50 MB)...\n")

try:
    # Dossier de cache Ultralytics
    cache_dir = Path.home() / ".cache" / "ultralytics"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = cache_dir / "yolov11m.pt"
    
    if model_path.exists() and model_path.stat().st_size > 10_000_000:  # > 10 MB
        print(f"✅ Modèle déjà téléchargé: {model_path}")
    else:
        if model_path.exists():
            model_path.unlink()  # Supprimer le fichier corrompu
        
        # URL du modèle
        model_url = "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov11m.pt"
        
        print(f"📥 Téléchargement vers: {model_path}")
        
        # Télécharger avec urllib
        def download_with_progress(url, filepath):
            """Télécharger avec barre de progression"""
            try:
                urllib.request.urlretrieve(url, filepath, reporthook=lambda block, size, total: 
                    print(f"\r  {min(100, int(block * size / total * 100))}%", end=''))
                print()
            except Exception as e:
                raise e
        
        try:
            download_with_progress(model_url, model_path)
            print(f"✅ Téléchargement terminé!")
        except Exception as e:
            print(f"⚠️  Téléchargement échoué: {e}")
            print("   Essai du lien alternatif...")
            # Essayer depuis un autre lien
            model_url_alt = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov11m.pt"
            try:
                download_with_progress(model_url_alt, model_path)
                print(f"✅ Téléchargement alternatif réussi!")
            except:
                print(f"❌ Les deux téléchargements ont échoué")
                raise
    
    # Vérifier que c'est bien chargé
    print("\n🧪 Test de chargement du modèle...")
    model_seg = YOLO(str(model_path), task='segment')
    print("✅ Modèle de segmentation chargé et prêt!")
    
    print("\n" + "=" * 80)
    print("✅ Prêt pour l'entraînement!")
    print("   Exécutez maintenant: python simple_train.py")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Solution manuelle:")
    print("   1. Téléchargez le fichier manuellement:")
    print("      https://github.com/ultralytics/assets/releases/tag/v0.0.0")
    print("   2. Placez yolov11m.pt dans:")
    print(f"      {cache_dir}")
    print("   3. Relancez le training: python simple_train.py")
    sys.exit(1)
