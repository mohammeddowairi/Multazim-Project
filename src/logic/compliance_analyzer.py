import cv2
import os
from ultralytics import YOLO

class ComplianceAnalyzer:
    def __init__(self, target_item="Ghotra"):
        """
        target_item: The specific dress code selected in the Admin Dashboard.
        Options: 'Ghotra', 'Mask', 'Helmet'
        """
        self.model = None
        self.confidence_threshold = 0.40 
        self.target_item = target_item

        # --- MODEL CONFIGURATION ---
        # This dictionary maps the Dashboard selection to the specific file and class names.
        self.MODEL_CONFIG = {
            "Ghotra": {
                "path": "models/ghotra_yolov5.pt",
                # We include multiple spellings to be safe
                "classes": ["ghotra", "shemagh", "gotrah", "traditional_clothes"]
            },
            "Mask": {
                "path": "models/mask_yolov5.pt",
                "classes": ["with_mask"] 
            },
            "Helmet": {
                "path": "models/helmet_yolov5.pt",
                "classes": ["helmet", "hardhat", "safety_helmet"]
            }
        }

        # 1. Select the configuration
        if target_item in self.MODEL_CONFIG:
            config = self.MODEL_CONFIG[target_item]
            self.model_path = config["path"]
            self.valid_classes = config["classes"]
        else:
            print(f"WARNING: Unknown item '{target_item}'. Defaulting to Ghotra.")
            self.model_path = "models/ghotra_yolov5.pt"
            self.valid_classes = ["ghotra", "shemagh", "traditional_clothes"]

        # 2. Load the model
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = YOLO(self.model_path)
                print(f"SUCCESS: Loaded model for {self.target_item} from {self.model_path}")
            except Exception as e:
                print(f"ERROR: Could not load model: {e}")
        else:
            print(f"WARNING: Model file not found at {self.model_path}")

    def check_compliance(self, frame):
        """
        Analyzes the frame.
        Returns: (processed_frame, status)
        """
        status = "NO ACCESS"
        display_frame = frame.copy()

        if self.model:
            # Run AI inference
            results = self.model(frame, verbose=False, conf=self.confidence_threshold)
            
            valid_detections = []

            # 1. Filter: Keep only the specific class we need
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                
                # Check if this object is in our allowed list for the current dress code
                if class_name.lower() in self.valid_classes:
                    valid_detections.append(box)

            # 2. Selection: Find the Closest User (Largest Box)
            if valid_detections:
                best_box = None
                max_area = 0

                for box in valid_detections:
                    coords = box.xyxy[0].cpu().numpy()
                    width = coords[2] - coords[0]
                    height = coords[3] - coords[1]
                    area = width * height
                    
                    if area > max_area:
                        max_area = area
                        best_box = box

                # 3. Draw ONLY the winner
                if best_box:
                    status = "ACCESS GRANTED"
                    
                    # Get coordinates
                    coords = best_box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                    
                    # Draw Green Box
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    
                    # Draw Label
                    label = f"{self.target_item.upper()} DETECTED"
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                    
                    # Draw text background
                    cv2.rectangle(display_frame, (x1, y1 - 30), (x1 + w, y1), (0, 255, 0), -1)
                    
                    # Draw text
                    cv2.putText(display_frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        return display_frame, status