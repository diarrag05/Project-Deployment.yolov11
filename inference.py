"""
Script d'inférence complet avec calcul automatique du taux de vides
Prédit sur une image/dossier et calcule le void_rate
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import json
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import torch

PROJECT_DIR = Path(__file__).parent
MODELS_DIR = PROJECT_DIR / "models"
INFERENCES_DIR = PROJECT_DIR / "inferences"

# Créer le répertoire d'inférences
INFERENCES_DIR.mkdir(exist_ok=True)

class InferenceWithVoidRate:
    """Classe pour effectuer l'inférence et calculer le void_rate"""
    
    def __init__(self, model_path: str, conf_threshold: float = 0.5):
        """
        Initialiser l'inférence
        
        Args:
            model_path: Chemin vers le modèle YOLOv11 .pt
            conf_threshold: Seuil de confiance pour les détections
        """
        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path, task="segment")
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.class_names = {0: 'chip', 1: 'hole'}
    
    def infer_image(self, image_path: str) -> Dict:
        """
        Effectuer l'inférence sur une image et calculer le void_rate
        
        Args:
            image_path: Chemin vers l'image
        
        Returns:
            Dictionnaire avec résultats et void_rate
        """
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            return {'error': f"Image non trouvée: {image_path}"}
        
        h, w = image.shape[:2]
        
        # Effectuer la prédiction
        results = self.model.predict(
            source=image_path,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False,
        )
        
        result = results[0] if results else None
        
        if result is None or result.masks is None or len(result.boxes) == 0:
            return {
                'image_path': str(image_path),
                'image_name': Path(image_path).name,
                'resolution': f"{w}x{h}",
                'num_detections': 0,
                'void_rate': 0.0,
                'hole_area_pixels': 0,
                'chip_area_pixels': 0,
                'detections': []
            }
        
        # Traiter les détections
        chip_area = 0
        holes_area = 0
        detections = []
        
        for i, (cls, conf, mask, box) in enumerate(
            zip(result.boxes.cls, result.boxes.conf, result.masks.data, result.boxes.xyxy)
        ):
            cls_id = int(cls.item())
            confidence = float(conf.item())
            mask_np = mask.cpu().numpy().astype(np.uint8) * 255
            mask_area = np.sum(mask_np > 0)
            
            # Coordonnées du box
            x1, y1, x2, y2 = [float(v.item()) for v in box]
            
            detection = {
                'id': i,
                'class': self.class_names.get(cls_id, f"class_{cls_id}"),
                'class_id': cls_id,
                'confidence': confidence,
                'area_pixels': int(mask_area),
                'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
            }
            
            if cls_id == 0:  # chip
                chip_area += mask_area
            elif cls_id == 1:  # hole
                holes_area += mask_area
            
            detections.append(detection)
        
        # Calculer le void_rate
        void_rate = (holes_area / chip_area * 100) if chip_area > 0 else 0.0
        
        return {
            'image_path': str(image_path),
            'image_name': Path(image_path).name,
            'resolution': f"{w}x{h}",
            'model_used': Path(self.model_path).name,
            'confidence_threshold': self.conf_threshold,
            'num_detections': len(detections),
            'chip_area_pixels': int(chip_area),
            'hole_area_pixels': int(holes_area),
            'void_rate': float(void_rate),
            'void_rate_percent': f"{void_rate:.2f}%",
            'detections': detections,
            'timestamp': datetime.now().isoformat(),
        }
    
    def infer_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        Effectuer l'inférence sur plusieurs images
        
        Args:
            image_paths: Liste des chemins vers les images
        
        Returns:
            Liste des résultats
        """
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"[{i}/{len(image_paths)}] Traitement: {Path(image_path).name}")
            result = self.infer_image(image_path)
            results.append(result)
            
            # Afficher le résultat
            if 'error' not in result:
                print(f"  ✓ Taux de vides: {result['void_rate_percent']}")
            else:
                print(f"  ✗ Erreur: {result['error']}")
        
        return results
    
    def infer_directory(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """
        Effectuer l'inférence sur toutes les images d'un répertoire
        
        Args:
            directory: Chemin du répertoire
            extensions: Extensions de fichiers
        
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
        
        image_files = sorted(image_files)
        
        print(f"\n📁 {len(image_files)} image(s) trouvée(s) dans {directory}\n")
        
        return self.infer_batch([str(f) for f in image_files])
    
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
            output_file = INFERENCES_DIR / f"inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            output_file = Path(output_file)
        
        # Calculer les statistiques
        valid_results = [r for r in results if 'error' not in r]
        void_rates = [r['void_rate'] for r in valid_results]
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'num_images_processed': len(results),
            'num_successful': len(valid_results),
            'num_errors': len(results) - len(valid_results),
            'stats': {
                'avg_void_rate': float(np.mean(void_rates)) if void_rates else 0,
                'min_void_rate': float(np.min(void_rates)) if void_rates else 0,
                'max_void_rate': float(np.max(void_rates)) if void_rates else 0,
                'std_void_rate': float(np.std(void_rates)) if void_rates else 0,
                'median_void_rate': float(np.median(void_rates)) if void_rates else 0,
            },
            'results': results
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=4)
        
        return str(output_file)
    
    def annotate_image(self, image_path: str, output_path: str = None) -> str:
        """
        Créer une image annotée avec les prédictions
        
        Args:
            image_path: Chemin vers l'image
            output_path: Chemin pour sauvegarder l'image annotée
        
        Returns:
            Chemin de l'image annotée
        """
        # Prédiction
        results = self.model.predict(
            source=image_path,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False,
        )
        
        # Plot annotated image
        result = results[0]
        annotated_image = result.plot()
        
        if output_path is None:
            output_path = INFERENCES_DIR / f"annotated_{Path(image_path).stem}.jpg"
        
        cv2.imwrite(str(output_path), annotated_image)
        print(f"\n📸 Image annotée sauvegardée: {output_path}")
        
        return str(output_path)
    
    def print_results_summary(self, results: List[Dict]):
        """Afficher un résumé des résultats"""
        valid_results = [r for r in results if 'error' not in r]
        void_rates = [r['void_rate'] for r in valid_results]
        
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES INFÉRENCES")
        print("=" * 80)
        print(f"Images traitées: {len(results)}")
        print(f"Succès: {len(valid_results)}")
        print(f"Erreurs: {len(results) - len(valid_results)}")
        
        if void_rates:
            print(f"\n{'Taux de vides (void_rate)':40}")
            print(f"  Moyen:  {np.mean(void_rates):.2f}%")
            print(f"  Min:    {np.min(void_rates):.2f}%")
            print(f"  Max:    {np.max(void_rates):.2f}%")
            print(f"  Médian: {np.median(void_rates):.2f}%")
            print(f"  Écart-type: {np.std(void_rates):.2f}%")
        
        print("=" * 80)
        
        # Top 5 images avec plus de vides
        if void_rates:
            top_void = sorted(
                valid_results,
                key=lambda x: x['void_rate'],
                reverse=True
            )[:5]
            
            print(f"\n🔴 Top 5 images avec plus de vides:")
            for i, result in enumerate(top_void, 1):
                print(f"  {i}. {result['image_name']}: {result['void_rate_percent']}")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Inférence avec calcul automatique du taux de vides"
    )
    parser.add_argument(
        "-i", "--image",
        help="Chemin vers une image spécifique"
    )
    parser.add_argument(
        "-d", "--directory",
        help="Chemin vers un répertoire d'images"
    )
    parser.add_argument(
        "-m", "--model",
        help="Chemin vers le modèle (sinon utilise le dernier)"
    )
    parser.add_argument(
        "-c", "--confidence",
        type=float,
        default=0.5,
        help="Seuil de confiance (défaut: 0.5)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Chemin pour sauvegarder les résultats JSON"
    )
    parser.add_argument(
        "-a", "--annotate",
        action="store_true",
        help="Sauvegarder les images annotées"
    )
    
    args = parser.parse_args()
    
    # Choisir le modèle
    if args.model:
        model_path = args.model
    else:
        models = list(MODELS_DIR.glob("*.pt"))
        if not models:
            print(f"❌ Aucun modèle trouvé dans: {MODELS_DIR}")
            return
        model_path = str(models[-1])
    
    print("=" * 80)
    print("🔍 INFÉRENCE AVEC CALCUL DU TAUX DE VIDES")
    print("=" * 80)
    print(f"Modèle: {Path(model_path).name}")
    print(f"Confiance: {args.confidence}")
    
    # Créer l'inférence
    inference = InferenceWithVoidRate(model_path, args.confidence)
    
    # Traiter les images
    results = []
    
    if args.image:
        print(f"\n📷 Image unique: {args.image}")
        result = inference.infer_image(args.image)
        results = [result]
        
        if 'error' not in result:
            print(f"\n✓ Taux de vides: {result['void_rate_percent']}")
            print(f"  Chips détectés: {len([d for d in result['detections'] if d['class'] == 'chip'])}")
            print(f"  Trous détectés: {len([d for d in result['detections'] if d['class'] == 'hole'])}")
        
        if args.annotate:
            inference.annotate_image(args.image)
    
    elif args.directory:
        print(f"\n📁 Répertoire: {args.directory}")
        results = inference.infer_directory(args.directory)
    
    else:
        # Utiliser le test set
        test_images_dir = PROJECT_DIR / "test" / "images"
        if test_images_dir.exists():
            print(f"\n📁 Test set: {test_images_dir}")
            results = inference.infer_directory(str(test_images_dir))
        else:
            print("❌ Aucune source d'image spécifiée et pas de test set trouvé")
            return
    
    # Sauvegarder les résultats
    if results:
        output_file = inference.save_results(results, args.output)
        print(f"\n💾 Résultats JSON: {output_file}")
        
        # Afficher le résumé
        inference.print_results_summary(results)
    
    print("\n✨ Inférence terminée!")


if __name__ == "__main__":
    main()
