from ultralytics import YOLO

if __name__ == '__main__':
    # Load model
    model = YOLO('yolov8n.pt') 

    # Train on GPU
    results = model.train(
        data='labassistant_dataset_v3/data.yaml', 
        epochs=50, 
        imgsz=640,
        device=0,  # <--- This forces GPU usage (0 is the first GPU)
        workers=0  # <--- Windows Fix: Set workers=0 to prevent "BrokenPipe" errors
    )

    model.export(format='onnx')


    