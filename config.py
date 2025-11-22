"""
Configuration avancée pour l'entraînement YOLOv11
Contient différents profils pour différents objectifs
"""

# ============================
# CONFIGURATION D'ENTRAÎNEMENT
# ============================

# Profil 1: Entraînement rapide (dev/test)
FAST_TRAINING = {
    "model_size": "n",          # Nano - très rapide
    "epochs": 10,               # Peu d'epochs pour tester
    "batch_size": 32,           # Batch grand
    "img_size": 416,            # Images petites
    "patience": 5,              # Early stopping rapide
    "learning_rate": 0.001,
    "lr_scheduler": "linear",
}

# Profil 2: Entraînement équilibré (recommandé)
BALANCED_TRAINING = {
    "model_size": "m",          # Medium
    "epochs": 100,              # Nombre d'epochs raisonnable
    "batch_size": 16,           # Batch standard
    "img_size": 640,            # Taille standard YOLO
    "patience": 20,             # Early stopping standard
    "learning_rate": 0.001,     # SGD learning rate
    "lr_scheduler": "cosine",   # Cosine annealing
    "weight_decay": 0.0005,
}

# Profil 3: Entraînement précis (haute performance)
HIGH_QUALITY_TRAINING = {
    "model_size": "l",          # Large
    "epochs": 150,              # Plus d'epochs
    "batch_size": 8,            # Batch petit = gradient plus précis
    "img_size": 1024,           # Images grandes
    "patience": 30,             # Early stopping patient
    "learning_rate": 0.0005,    # LR plus faible
    "lr_scheduler": "cosine",
    "weight_decay": 0.001,      # Régularisation forte
}

# Profil 4: Entraînement production (modèle XL)
PRODUCTION_TRAINING = {
    "model_size": "x",          # Extra Large
    "epochs": 200,              # Beaucoup d'epochs
    "batch_size": 4,            # Batch très petit
    "img_size": 1280,           # Très grandes images
    "patience": 50,             # Très patient
    "learning_rate": 0.0001,    # LR très faible
    "lr_scheduler": "cosine",
    "weight_decay": 0.001,
}

# ============================
# PARAMÈTRES D'AUGMENTATION
# ============================

# Augmentation légère (pour données limitées)
LIGHT_AUGMENTATION = {
    "mosaic": 0.7,
    "hsv_h": 0.015,
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "degrees": 5.0,
    "translate": 0.05,
    "scale": 0.3,
    "flipud": 0.3,
    "fliplr": 0.3,
    "perspective": 0.0,
    "copy_paste": 0.0,
}

# Augmentation standard (par défaut)
STANDARD_AUGMENTATION = {
    "mosaic": 1.0,
    "hsv_h": 0.015,
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "degrees": 10.0,
    "translate": 0.1,
    "scale": 0.5,
    "flipud": 0.5,
    "fliplr": 0.5,
    "perspective": 0.0,
    "copy_paste": 0.0,
}

# Augmentation agressive (pour petits datasets)
AGGRESSIVE_AUGMENTATION = {
    "mosaic": 1.0,
    "hsv_h": 0.05,
    "hsv_s": 0.8,
    "hsv_v": 0.5,
    "degrees": 15.0,
    "translate": 0.15,
    "scale": 0.8,
    "flipud": 0.5,
    "fliplr": 0.5,
    "perspective": 0.01,
    "copy_paste": 0.1,
}

# ============================
# STRATÉGIES D'OPTIMISEURS
# ============================

# SGD: Stochastic Gradient Descent (plus stable)
SGD_CONFIG = {
    "optimizer": "SGD",
    "lr0": 0.001,
    "momentum": 0.937,
}

# Adam: Plus rapide à converger
ADAM_CONFIG = {
    "optimizer": "Adam",
    "lr0": 0.001,
    "beta1": 0.9,
    "beta2": 0.999,
}

# ============================
# PRESETS POUR CAS D'USAGE
# ============================

# Pour prototype/expérimentation
QUICK_START = {
    **FAST_TRAINING,
    **LIGHT_AUGMENTATION,
    "optimizer": "SGD",
}

# Pour production (recommandé)
PRODUCTION_PRESET = {
    **BALANCED_TRAINING,
    **STANDARD_AUGMENTATION,
    "optimizer": "SGD",
    "close_mosaic": 10,
    "warmup_epochs": 3,
}

# Pour données limitées
LIMITED_DATA_PRESET = {
    "model_size": "m",
    "epochs": 200,
    "batch_size": 8,
    "img_size": 640,
    "patience": 50,
    "learning_rate": 0.0005,
    "lr_scheduler": "cosine",
    "weight_decay": 0.001,
    **AGGRESSIVE_AUGMENTATION,  # Augmentation forte
    "copy_paste": 0.2,  # Copy-paste augmentation
    "optimizer": "SGD",
}

# Pour GPU avec mémoire limitée
MEMORY_EFFICIENT_PRESET = {
    "model_size": "s",
    "epochs": 100,
    "batch_size": 4,
    "img_size": 480,
    "patience": 20,
    "learning_rate": 0.001,
    "lr_scheduler": "cosine",
    "weight_decay": 0.0005,
    **STANDARD_AUGMENTATION,
    "optimizer": "SGD",
}

# ============================
# SEUILS D'ÉVALUATION
# ============================

EVALUATION_THRESHOLDS = {
    # Seuils de confiance pour les détections
    "conf_threshold": 0.5,      # Confiance minimale
    "iou_threshold": 0.45,      # IoU minimal pour NMS
    
    # Critères de succès
    "min_map50": 0.75,          # mAP50 minimal attendu
    "min_map50_95": 0.65,       # mAP50-95 minimal
    "min_precision": 0.85,      # Précision minimale
    "min_recall": 0.80,         # Rappel minimal
}

# ============================
# PARAMÈTRES D'INFÉRENCE
# ============================

INFERENCE_CONFIG = {
    "conf_threshold": 0.5,      # Seuil de confiance
    "iou_threshold": 0.45,      # NMS IoU
    "max_detections": 300,      # Max détections par image
    "agnostic": False,          # Class-agnostic NMS
}

# ============================
# HELPER FUNCTIONS
# ============================

def get_config_for_dataset_size(num_images: int):
    """Recommander une configuration basée sur la taille du dataset"""
    if num_images < 100:
        return LIMITED_DATA_PRESET
    elif num_images < 1000:
        return BALANCED_TRAINING
    else:
        return HIGH_QUALITY_TRAINING

def get_config_for_gpu_memory(memory_gb: int):
    """Recommander une configuration basée sur la mémoire GPU"""
    if memory_gb < 4:
        return MEMORY_EFFICIENT_PRESET
    elif memory_gb < 8:
        return BALANCED_TRAINING
    else:
        return PRODUCTION_TRAINING

# ============================
# EXEMPLE D'USAGE
# ============================

if __name__ == "__main__":
    import json
    
    print("=== CONFIGURATIONS DISPONIBLES ===\n")
    
    configs = {
        "QUICK_START": QUICK_START,
        "BALANCED_TRAINING": BALANCED_TRAINING,
        "HIGH_QUALITY_TRAINING": HIGH_QUALITY_TRAINING,
        "PRODUCTION_TRAINING": PRODUCTION_TRAINING,
        "LIMITED_DATA_PRESET": LIMITED_DATA_PRESET,
        "MEMORY_EFFICIENT_PRESET": MEMORY_EFFICIENT_PRESET,
    }
    
    for name, config in configs.items():
        print(f"\n📋 {name}:")
        print(json.dumps(config, indent=2))
