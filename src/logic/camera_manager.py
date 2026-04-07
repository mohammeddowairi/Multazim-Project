import cv2

class CameraManager:
    def __init__(self, source=0):
        self.source = source
        self.cap = None
        self.is_running = False

    def start(self):
        """Opens the camera connection using Windows Media Foundation (MSMF)"""
        print(f"Initializing camera source: {self.source}")
        
        # 1. FORCE THE MODERN WINDOWS DRIVER (CAP_MSMF)
        # This matches how the Windows Camera App connects.
        self.cap = cv2.VideoCapture(self.source, cv2.CAP_MSMF)
        
        if not self.cap.isOpened():
            print(f"ERROR: Could not open camera {self.source}.")
            self.is_running = False
            return False
        
        # 2. FORCE 'MJPEG' FORMAT (CRITICAL FOR GLITCHES)
        # Glitches happen when the camera sends raw data too fast. 
        # MJPEG compresses it, making the video smooth and clear.
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)

        # 3. FORCE STANDARD RESOLUTION
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.is_running = True
        print("Camera started successfully.")
        return True

    def get_frame(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def stop(self):
        if self.cap:
            self.cap.release()
        self.is_running = False
        print("Camera released.")

# --- RUN THIS BLOCK TO TEST IT IMMEDIATELY ---
if __name__ == "__main__":
    # Try source=0 first. If it fails, change to source=1
    cam = CameraManager(source=0)
    
    if cam.start():
        print("✅ Camera is live! Press 'q' to exit.")
        while True:
            frame = cam.get_frame()
            
            if frame is None:
                print("Wait...")
                continue
                
            cv2.imshow("Fixed Camera (MSMF + MJPG)", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        print("❌ Failed to start. Try changing 'source=0' to 'source=1' in the code.")

    cam.stop()
    cv2.destroyAllWindows()