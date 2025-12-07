"""
Script de calcul du taux de vides (void_rate)
void_rate = (somme des aires de trous / aire du composant) * 100

Utilise les masks de segmentation du modèle YOLOv11
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import json
from datetime import datetime
from typing import Dict, List, Tuple
import torch

PROJECT_DIR = Path(__file__).parent
MODELS_DIR = PROJECT_DIR / "models"
RESULTS_DIR = PROJECT_DIR / "void_rate_results"

# Créer le répertoire de résultats
RESULTS_DIR.mkdir(exist_ok=True)

class VoidRateCalculator:
    """Classe pour calculer le taux de vides"""
    
    def __init__(self, model_path: str):
        """
        Initialiser le calculateur
        
        Args:
            model_path: Chemin vers le modèle YOLOv11 .pt
        """
        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path, task="segment")
        self.model_path = model_path
    
    def predict_masks(self, image_path: str, conf_threshold: float = 0.5):
        """
        Prédire les masks pour une image
        
        Args:
            image_path: Chemin vers l'image
            conf_threshold: Seuil de confiance
        
        Returns:
            Résultats de prédiction
        """
        results = self.model.predict(
            source=image_path,
            conf=conf_threshold,
            device=self.device,
            verbose=False,
        )
        return results[0] if results else None
    
    def calculate_mask_area(self, mask: np.ndarray) -> int:
        """
        Calculer l'aire d'un mask (nombre de pixels)
        
        Args:
            mask: Array binaire du mask
        
        Returns:
            Nombre de pixels du mask
        """
        return np.sum(mask > 0)
    
    def calculate_void_rate(
        self,
        image_path: str,
        conf_threshold: float = 0.5,
        verbose: bool = True
    ) -> Dict:
        """
        Calculer le taux de vides pour une image
        
        void_rate = (somme des aires de trous / aire du composant) * 100
        
        Args:
            image_path: Chemin vers l'image
            conf_threshold: Seuil de confiance
            verbose: Afficher les détails
        
        Returns:
            Dictionnaire avec les résultats
        """
        result = self.predict_masks(image_path, conf_threshold)
        
        if result is None or result.masks is None:
            return {
                'image': str(image_path),
                'void_rate': 0.0,
                'hole_area_pixels': 0,
                'chip_area_pixels': 0,
                'num_holes': 0,
                'num_chips': 0,
                'error': 'Aucune détection',
                'yolo_results': [result] if result else None
            }
        
        image = cv2.imread(image_path)
        h, w = image.shape[:2]
        
        # Séparation des classes
        chip_area = 0
        holes_area = 0
        num_chips = 0
        num_holes = 0
        
        # Classes: 0 = chip, 1 = hole
        for cls, conf, mask in zip(result.boxes.cls, result.boxes.conf, result.masks.data):
            cls = int(cls.item())
            mask_np = mask.cpu().numpy().astype(np.uint8) * 255
            mask_area = self.calculate_mask_area(mask_np)
            
            if cls == 0:  # chip
                chip_area += mask_area
                num_chips += 1
            elif cls == 1:  # hole
                holes_area += mask_area
                num_holes += 1
        
        # Calculer le taux de vides
        if chip_area > 0:
            void_rate = (holes_area / chip_area) * 100
        else:
            void_rate = 0.0
        
        result_dict = {
            'image': str(image_path),
            'void_rate': float(void_rate),
            'hole_area_pixels': int(holes_area),
            'chip_area_pixels': int(chip_area),
            'num_holes': int(num_holes),
            'num_chips': int(num_chips),
            'image_resolution': f"{w}x{h}",
            'confidence_threshold': conf_threshold,
            'yolo_results': [result]  # Include YOLO results for mask generation
        }
        
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Image: {Path(image_path).name}")
            print(f"{'=' * 60}")
            print(f"Aire du composant (chip): {chip_area:,} pixels")
            print(f"Aire des trous (holes): {holes_area:,} pixels")
            print(f"Nombre de chips détectés: {num_chips}")
            print(f"Nombre de holes détectés: {num_holes}")
            print(f"TAUX DE VIDES: {void_rate:.2f}%")
            print(f"{'=' * 60}")
        
        return result_dict
    
    def process_directory(
        self,
        directory: str,
        conf_threshold: float = 0.5,
        extensions: List[str] = None
    ) -> List[Dict]:
        """
        Traiter toutes les images d'un répertoire
        
        Args:
            directory: Chemin du répertoire
            conf_threshold: Seuil de confiance
            extensions: Extensions de fichiers à traiter
        
        Returns:
            Liste des résultats
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        dir_path = Path(directory)
        image_files = []
        
        for ext in extensions:
            image_files.extend(dir_path.glob(f"*{ext}"))
            image_files.extend(dir_path.glob(f"*{ext.upper()}"))
        
        print(f"\n📁 Traitement de {len(image_files)} image(s) dans {directory}")
        
        results = []
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}]", end=" ")
            result = self.calculate_void_rate(str(image_path), conf_threshold, verbose=True)
            results.append(result)
        
        return results
    
    def process_test_set(self, conf_threshold: float = 0.5) -> List[Dict]:
        """
        Traiter le test set complet
        
        Args:
            conf_threshold: Seuil de confiance
        
        Returns:
            Liste des résultats
        """
        test_images_dir = PROJECT_DIR / "test" / "images"
        
        if not test_images_dir.exists():
            print(f"❌ Répertoire test/images introuvable: {test_images_dir}")
            return []
        
        return self.process_directory(str(test_images_dir), conf_threshold)
    
    def save_results(self, results: List[Dict], output_file: str = None) -> str:
        """
        Sauvegarder les résultats en JSON
        
        Args:
            results: Liste des résultats
            output_file: Chemin du fichier de sortie
        
        Returns:
            Chemin du fichier sauvegardé
        """
        if output_file is None:
            output_file = RESULTS_DIR / f"void_rate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            output_file = Path(output_file)
        
        # Calculer les statistiques
        void_rates = [r['void_rate'] for r in results if 'error' not in r]
        stats = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'num_images': len(results),
            'avg_void_rate': float(np.mean(void_rates)) if void_rates else 0,
            'min_void_rate': float(np.min(void_rates)) if void_rates else 0,
            'max_void_rate': float(np.max(void_rates)) if void_rates else 0,
            'std_void_rate': float(np.std(void_rates)) if void_rates else 0,
            'results': results
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=4)
        
        print(f"\n💾 Résultats sauvegardés: {output_file}")
        
        # Afficher les statistiques
        print(f"\n{'=' * 60}")
        print("📊 STATISTIQUES - TAUX DE VIDES")
        print(f"{'=' * 60}")
        print(f"Nombre d'images: {len(results)}")
        print(f"Taux moyen: {stats['avg_void_rate']:.2f}%")
        print(f"Taux min: {stats['min_void_rate']:.2f}%")
        print(f"Taux max: {stats['max_void_rate']:.2f}%")
        print(f"Écart-type: {stats['std_void_rate']:.2f}%")
        print(f"{'=' * 60}")
        
        return str(output_file)
    
    def visualize_results(
        self,
        image_path: str,
        output_path: str = None,
        conf_threshold: float = 0.5
    ) -> str:
        """
        Visualiser les prédictions avec les masks
        
        Args:
            image_path: Chemin vers l'image
            output_path: Chemin pour sauvegarder l'image annotée
            conf_threshold: Seuil de confiance
        
        Returns:
            Chemin de l'image sauvegardée
        """
        result = self.predict_masks(image_path, conf_threshold)
        
        if result is None:
            print("❌ Aucune détection")
            return None
        
        # Sauvegarder l'image annotée
        image_array = result.plot()
        
        if output_path is None:
            output_path = RESULTS_DIR / f"annotated_{Path(image_path).stem}.jpg"
        
        cv2.imwrite(str(output_path), image_array)
        print(f"📸 Image annotée sauvegardée: {output_path}")
        
        return str(output_path)


def main():
    """Fonction principale"""
    
    print("=" * 80)
    print("🔍 CALCUL DU TAUX DE VIDES (VOID RATE)")
    print("=" * 80)
    
    # Chercher le meilleur modèle
    models = list(MODELS_DIR.glob("*.pt"))
    if not models:
        print(f"❌ Aucun modèle trouvé dans: {MODELS_DIR}")
        return
    
    model_path = str(models[-1])  # Prendre le dernier modèle
    print(f"\n📥 Modèle utilisé: {Path(model_path).name}")
    
    # Créer le calculateur
    calculator = VoidRateCalculator(model_path)
    
    # Traiter le test set
    results = calculator.process_test_set(conf_threshold=0.5)
    
    # Sauvegarder les résultats
    if results:
        calculator.save_results(results)
    
    # Visualiser quelques résultats
    test_images_dir = PROJECT_DIR / "test" / "images"
    if test_images_dir.exists():
        sample_images = list(test_images_dir.glob("*.jpg"))[:3]
        
        if sample_images:
            print(f"\n📸 Visualisation de {len(sample_images)} image(s)...")
            for image_path in sample_images:
                calculator.visualize_results(str(image_path))


if __name__ == "__main__":
    main()
