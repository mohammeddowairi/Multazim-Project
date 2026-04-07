import cv2
import time

def test_cameras():
    print("SEARCHING FOR CAMERAS... (This might take 10-20 seconds)")
    print("-" * 50)
    
    # Check first 10 indexes
    available_cameras = []
    
    for index in range(10):
        # Try to open the camera with DirectShow (crucial for Windows)
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) 
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                print(f"[SUCCESS] Camera found at Index {index} | Resolution: {w}x{h}")
                available_cameras.append(index)
            else:
                print(f"[WARNING] Camera at Index {index} opened, but returned no image (Black/Static).")
        
        cap.release()
    
    print("-" * 50)
    if not available_cameras:
        print("❌ NO CAMERAS FOUND. Please check your USB connection or Privacy Settings.")
    else:
        print(f"✅ WORKING CAMERAS: {available_cameras}")
        print(f"👉 Update your code to use: source={available_cameras[0]}")

if __name__ == "__main__":
    test_cameras()