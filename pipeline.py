"""
Pipeline complet d'entraînement, évaluation et inférence
Intègre automatiquement les meilleures pratiques
"""

import sys
from pathlib import Path
from datetime import datetime
import json

from train import train_yolov11_segmentation, print_metrics
from evaluate import evaluate_model
from inference import InferenceWithVoidRate
from config import (
    BALANCED_TRAINING,
    STANDARD_AUGMENTATION,
)

PROJECT_DIR = Path(__file__).parent
MODELS_DIR = PROJECT_DIR / "models"
LOGS_DIR = PROJECT_DIR / "logs"

LOGS_DIR.mkdir(exist_ok=True)

def log_pipeline_step(step_name: str, status: str, message: str = ""):
    """Enregistrer une étape du pipeline"""
    timestamp = datetime.now().isoformat()
    log_file = LOGS_DIR / "pipeline.log"
    
    log_entry = f"[{timestamp}] {step_name}: {status}"
    if message:
        log_entry += f" - {message}"
    
    print(log_entry)
    
    with open(log_file, "a") as f:
        f.write(log_entry + "\n")

def run_full_pipeline(
    use_config: str = "BALANCED",
    skip_training: bool = False,
    skip_evaluation: bool = False,
    skip_inference: bool = False,
    model_path: str = None,
):
    """
    Exécuter le pipeline complet
    
    Args:
        use_config: Configuration à utiliser (BALANCED, FAST, HIGH_QUALITY, etc.)
        skip_training: Sauter l'entraînement
        skip_evaluation: Sauter l'évaluation
        skip_inference: Sauter l'inférence
        model_path: Chemin vers un modèle existant
    """
    
    print("=" * 80)
    print("🔄 PIPELINE COMPLET YOLOv11-SEGMENTATION")
    print("=" * 80)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log = {
        "timestamp": timestamp,
        "steps": {}
    }
    
    # ====== ENTRAÎNEMENT ======
    if not skip_training and not model_path:
        print("\n" + "=" * 80)
        print("1️⃣  ENTRAÎNEMENT")
        print("=" * 80)
        
        try:
            log_pipeline_step("TRAINING", "STARTED", f"Config: {use_config}")
            
            # Obtenir la configuration
            if use_config == "BALANCED":
                from config import BALANCED_TRAINING
                config = BALANCED_TRAINING.copy()
            else:
                from config import (
                    FAST_TRAINING,
                    HIGH_QUALITY_TRAINING,
                    PRODUCTION_TRAINING,
                )
                configs = {
                    "FAST": FAST_TRAINING,
                    "HIGH_QUALITY": HIGH_QUALITY_TRAINING,
                    "PRODUCTION": PRODUCTION_TRAINING,
                }
                config = configs.get(use_config, BALANCED_TRAINING).copy()
            
            # Ajouter augmentation
            config.update(STANDARD_AUGMENTATION)
            
            # Entraîner
            model, results, run_dir = train_yolov11_segmentation(**config)
            
            # Récupérer le chemin du meilleur modèle
            best_model = run_dir / "weights" / "best.pt"
            model_path = str(best_model) if best_model.exists() else None
            
            log_pipeline_step("TRAINING", "COMPLETED", f"Model: {model_path}")
            
            run_log["steps"]["training"] = {
                "status": "completed",
                "model": str(model_path),
                "run_dir": str(run_dir),
            }
            
        except Exception as e:
            log_pipeline_step("TRAINING", "FAILED", str(e))
            run_log["steps"]["training"] = {"status": "failed", "error": str(e)}
            print(f"\n❌ Erreur d'entraînement: {e}")
            sys.exit(1)
    
    elif not model_path:
        # Chercher le meilleur modèle existant
        models = sorted(MODELS_DIR.glob("*.pt"), key=lambda x: x.stat().st_mtime, reverse=True)
        if models:
            model_path = str(models[0])
            print(f"\n📦 Utilisation du modèle existant: {Path(model_path).name}")
        else:
            print("❌ Aucun modèle trouvé")
            sys.exit(1)
    
    # ====== ÉVALUATION ======
    if not skip_evaluation and model_path:
        print("\n" + "=" * 80)
        print("2️⃣  ÉVALUATION")
        print("=" * 80)
        
        try:
            log_pipeline_step("EVALUATION", "STARTED", f"Model: {Path(model_path).name}")
            
            results, metrics = evaluate_model(model_path)
            
            log_pipeline_step("EVALUATION", "COMPLETED")
            
            run_log["steps"]["evaluation"] = {
                "status": "completed",
                "metrics": metrics,
            }
            
        except Exception as e:
            log_pipeline_step("EVALUATION", "FAILED", str(e))
            run_log["steps"]["evaluation"] = {"status": "failed", "error": str(e)}
            print(f"\n⚠ Erreur d'évaluation (non bloquant): {e}")
    
    # ====== INFÉRENCE & VOID_RATE ======
    if not skip_inference and model_path:
        print("\n" + "=" * 80)
        print("3️⃣  INFÉRENCE & CALCUL DU TAUX DE VIDES")
        print("=" * 80)
        
        try:
            log_pipeline_step("INFERENCE", "STARTED", f"Model: {Path(model_path).name}")
            
            # Créer l'inférence
            inference = InferenceWithVoidRate(model_path, conf_threshold=0.5)
            
            # Traiter le test set
            test_images_dir = PROJECT_DIR / "test" / "images"
            if test_images_dir.exists():
                results = inference.infer_directory(str(test_images_dir))
                
                # Sauvegarder
                output_file = inference.save_results(results)
                
                # Résumé
                inference.print_results_summary(results)
                
                log_pipeline_step("INFERENCE", "COMPLETED", f"Images: {len(results)}")
                
                run_log["steps"]["inference"] = {
                    "status": "completed",
                    "num_images": len(results),
                    "results_file": output_file,
                }
                
            else:
                print(f"⚠ Répertoire test/images introuvable: {test_images_dir}")
        
        except Exception as e:
            log_pipeline_step("INFERENCE", "FAILED", str(e))
            run_log["steps"]["inference"] = {"status": "failed", "error": str(e)}
            print(f"\n⚠ Erreur d'inférence (non bloquant): {e}")
    
    # ====== RÉSUMÉ ======
    print("\n" + "=" * 80)
    print("✅ PIPELINE TERMINÉ")
    print("=" * 80)
    
    # Sauvegarder le log du pipeline
    pipeline_log_file = LOGS_DIR / f"pipeline_{timestamp}.json"
    with open(pipeline_log_file, "w") as f:
        json.dump(run_log, f, indent=4)
    
    print(f"\n📝 Logs: {pipeline_log_file}")
    print(f"📊 Modèle final: {model_path}")
    
    return model_path, run_log

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline complet YOLOv11")
    parser.add_argument(
        "-c", "--config",
        default="BALANCED",
        choices=["FAST", "BALANCED", "HIGH_QUALITY", "PRODUCTION"],
        help="Configuration à utiliser"
    )
    parser.add_argument(
        "-m", "--model",
        help="Chemin vers un modèle existant (saute l'entraînement)"
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Sauter l'entraînement"
    )
    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Sauter l'évaluation"
    )
    parser.add_argument(
        "--skip-inference",
        action="store_true",
        help="Sauter l'inférence"
    )
    
    args = parser.parse_args()
    
    # Exécuter le pipeline
    model_path, log = run_full_pipeline(
        use_config=args.config,
        skip_training=args.skip_training,
        skip_evaluation=args.skip_evaluation,
        skip_inference=args.skip_inference,
        model_path=args.model,
    )
    
    print("\n🎉 Pipeline exécuté avec succès!")

if __name__ == "__main__":
    main()
