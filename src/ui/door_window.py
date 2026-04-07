import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import time
import os
from src.logic.compliance_analyzer import ComplianceAnalyzer
from src.logic.camera_manager import CameraManager
from src.logic.database_manager import DatabaseManager

class DoorAccessWindow(tk.Toplevel):
    def __init__(self, parent, admin_id, required_item):
        super().__init__(parent)
        self.parent = parent  # Reference to Dashboard for the restart trick
        self.admin_id = admin_id
        self.required_item = required_item 
        self.db = DatabaseManager()
        
        self.title(f"Multazim - Live Gate: {required_item}")
        self.geometry("1000x950")
        self.configure(bg="#f0f0f0")

        # --- SETTINGS ---
        self.REQUIRED_HOLD_DURATION = 1.2   # 1.2 seconds countdown
        self.state = "IDLE"
        self.gotrah_timer_start = None
        self.frozen_frame = None

        # --- UI SETUP ---
        self.status_label = tk.Label(self, text=f"Please wear your: {required_item}", 
                                     font=("Helvetica", 24, "bold"), bg="#f0f0f0", fg="#333")
        self.status_label.pack(pady=20)

        self.video_frame = tk.Label(self, bg="black")
        self.video_frame.pack(padx=20, pady=10)

        # BUTTON AREA
        self.btn_frame = tk.Frame(self, bg="#f0f0f0")
        self.btn_frame.pack(pady=20)

        # 1. START SCAN BUTTON
        self.start_btn = tk.Button(self.btn_frame, text="START SCANNING", 
                                  font=("Helvetica", 14, "bold"), bg="#007bff", fg="white", 
                                  width=20, height=2, command=self.start_scan)
        self.start_btn.pack(side="left", padx=10)

        # 2. NEXT USER / RESTART BUTTON
        self.reset_btn = tk.Button(self.btn_frame, text="NEXT USER (RESTART)", 
                                  font=("Helvetica", 14, "bold"), bg="#27ae60", fg="white", 
                                  width=20, height=2, command=self.reset_gate)
        self.reset_btn.pack(side="left", padx=10)

        # --- SYSTEM INIT ---
        try:
            self.analyzer = ComplianceAnalyzer(target_item=self.required_item)
            self.camera = CameraManager(source=0)
            self.camera.start()
        except Exception as e:
            messagebox.showerror("Error", f"Initialization Failed: {e}")
            self.destroy()
            return
        
        self.update_loop()

    def start_scan(self):
        """Prepares the UI for scanning"""
        self.state = "DETECTING"
        self.start_btn.config(state="disabled", text="SCANNING...", bg="#95a5a6")
        self.status_label.config(text="Searching...", fg="#d35400")

    def reset_gate(self):
        """The 'Clean Restart' method to avoid freezes"""
        aid = self.admin_id
        item = self.required_item
        self.destroy() # Kills camera and old memory
        
        # Re-open fresh window from the dashboard parent
        from src.ui.door_window import DoorAccessWindow
        DoorAccessWindow(self.parent, aid, item)

    def update_loop(self):
        if not self.winfo_exists(): return

        # --- STATE 1: SUCCESS (STAY FROZEN) ---
        if self.state == "SUCCESS":
            if self.frozen_frame is not None:
                self.render_frame(self.frozen_frame)
            self.after(30, self.update_loop)
            return

        # --- STATE 2: LIVE CAMERA FEED ---
        frame = self.camera.get_frame()
        if frame is not None:
            current_display = frame.copy()

            if self.state == "DETECTING":
                processed, result = self.analyzer.check_compliance(frame)
                current_display = processed

                if result == "ACCESS GRANTED":
                    # Initialize timer if this is the first frame of detection
                    if self.gotrah_timer_start is None:
                        self.gotrah_timer_start = time.time()
                    
                    elapsed = time.time() - self.gotrah_timer_start
                    
                    if elapsed >= self.REQUIRED_HOLD_DURATION:
                        # --- COUNTDOWN FINISHED ---
                        self.state = "SUCCESS"
                        self.frozen_frame = current_display.copy()
                        self.status_label.config(text="ACCESS GRANTED ✅", fg="white", bg="#2c3e50")
                        self.db.log_access(self.admin_id, self.required_item, "GRANTED")
                        # Show the winning frame and stop the loop processing
                        self.render_frame(self.frozen_frame)
                        self.after(30, self.update_loop)
                        return
                    else:
                        # --- COUNTDOWN IN PROGRESS ---
                        remaining = self.REQUIRED_HOLD_DURATION - elapsed
                        self.status_label.config(
                            text=f"Hold Still... {remaining:.1f}s", 
                            fg="#27ae60", 
                            bg="#f0f0f0"
                        )
                else:
                    # Item lost/not detected, reset timer
                    self.gotrah_timer_start = None
                    self.status_label.config(text="Scanning...", fg="#d35400")

            self.render_frame(current_display)

        self.after(30, self.update_loop)

    def render_frame(self, frame):
        """Converts BGR to RGB and pushes to Tkinter Label"""
        try:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        except:
            pass

    def destroy(self):
        """Safety cleanup for camera hardware"""
        if hasattr(self, 'camera'):
            self.camera.stop()
        super().destroy()