import cv2
import os
from ultralytics import YOLO
from src.logic.hardware_manager import HardwareManager

class ComplianceAnalyzer:
    def __init__(self, target_item="Ghotra"):
        self.model = None
        self.confidence_threshold = 0.50
        self.target_item = target_item
        # Initialized for reference, but not triggered in check_compliance
        self.hardware = HardwareManager(port='COM3') 

        self.MODEL_CONFIG = {
            "Ghotra": {"path": "models/ghotra_yolov5.pt", "classes": ["ghotra", "shemagh", "traditional_clothes"]},
            "Mask": {"path": "models/mask_yolov5.pt", "classes": ["nomask", "mask", "with_mask", "without_mask"]},
            "Helmet": {"path": "models/helmet_yolov5.pt", "classes": ["helmet", "hardhat", "safety_helmet"]}
        }

        config = self.MODEL_CONFIG.get(target_item, self.MODEL_CONFIG["Ghotra"])
        self.model_path = config["path"]
        self.valid_classes = config["classes"]
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = YOLO(self.model_path)
                print(f"SUCCESS: Loaded model for {self.target_item}")
            except Exception as e:
                print(f"ERROR: {e}")

    def check_compliance(self, frame):
        status = "NO ACCESS"
        display_frame = frame.copy()

        if self.model:
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            valid_detections = []

            if results and len(results) > 0:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    class_name = self.model.names[cls_id].lower()
                    if class_name in self.valid_classes:
                        valid_detections.append(box)

            if valid_detections:
                best_box = max(valid_detections, key=lambda b: (b.xyxy[0][2]-b.xyxy[0][0]) * (b.xyxy[0][3]-b.xyxy[0][1]))
                if best_box:
                    status = "ACCESS GRANTED"
                    coords = best_box.xyxy[0].cpu().numpy().astype(int)
                    cv2.rectangle(display_frame, (coords[0], coords[1]), (coords[2], coords[3]), (0, 255, 0), 4)
        
        return display_frame, status
