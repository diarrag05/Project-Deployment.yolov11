"""
Simple training script for YOLOv11 segmentation
"""
from ultralytics import YOLO

def main():
    # Load pre-trained model
    model = YOLO("models/yolo11s-seg.pt")

    # Training configuration
    results = model.train(
        data='dataset/data.yaml',
        epochs=100,
        batch=8,
        imgsz=640,
        device='cpu',  # Use 'cuda' if you have GPU
        optimizer='AdamW',
        lr0=0.001,
        patience=30,  # Early stopping

        # Data augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
        copy_paste=0.0,

        # Loss weights
        box=7.5,
        cls=0.5,
        dfl=1.5,

        # Other settings
        amp=False,  # Disable AMP for stability
        workers=8,
        project='runs/segment',
        name='train',
    )

    print("\n" + "="*60)
    print("Training completed!")
    print(f"Best model saved at: runs/segment/train/weights/best.pt")
    print("="*60)

if __name__ == "__main__":
    main()
