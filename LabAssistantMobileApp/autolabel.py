from ultralytics import YOLO
import os

# 1. Load your trained model
model = YOLO('runs/detect/train3/weights/best.pt') 

# 2. Path to your NEW, unlabeled images
source_dir = './new_hardware_photos'

# 3. Run inference
# save_txt=True: Generates the annotation files Roboflow needs
# conf=0.5: Only keep high-confidence guesses to save you cleanup time
results = model.predict(source=source_dir, save=True, save_txt=True, conf=0.5, save_conf=False)

print(f"✅ Done! Labels are in 'runs/detect/predict/labels'.")