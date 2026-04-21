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
        self.parent = parent 
        self.admin_id = admin_id
        self.required_item = required_item 
        self.db = DatabaseManager()
        
        self.title(f"Multazim - Live Gate: {required_item}")
        self.geometry("1000x950")
        self.configure(bg="#f0f0f0")

        # --- SETTINGS ---
        self.REQUIRED_HOLD_DURATION = 1.2    
        self.MAX_SCAN_DURATION = 20.0       
        
        self.state = "IDLE"
        self.gotrah_timer_start = None
        self.scan_start_time = None         
        self.frozen_frame = None

        # --- UI SETUP ---
        self.status_label = tk.Label(self, text=f"Please wear your: {required_item}", 
                                     font=("Helvetica", 24, "bold"), bg="#f0f0f0", fg="#333")
        self.status_label.pack(pady=20)


        self.timer_label = tk.Label(self, text="", font=("Helvetica", 14), bg="#f0f0f0", fg="#e74c3c")
        self.timer_label.pack()

        self.video_frame = tk.Label(self, bg="black")
        self.video_frame.pack(padx=20, pady=10)

        self.btn_frame = tk.Frame(self, bg="#f0f0f0")
        self.btn_frame.pack(pady=20)

        self.start_btn = tk.Button(self.btn_frame, text="START SCANNING", 
                                  font=("Helvetica", 14, "bold"), bg="#007bff", fg="white", 
                                  width=20, height=2, command=self.start_scan)
        self.start_btn.pack(side="left", padx=10)

        self.reset_btn = tk.Button(self.btn_frame, text="NEXT USER (RESTART)", 
                                  font=("Helvetica", 14, "bold"), bg="#27ae60", fg="white", 
                                  width=20, height=2, command=self.reset_gate)
        self.reset_btn.pack(side="left", padx=10)

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
        self.state = "DETECTING"
        self.scan_start_time = time.time() 
        self.start_btn.config(state="disabled", text="SCANNING...", bg="#95a5a6")
        self.status_label.config(text="Searching...", fg="#d35400")

    def reset_gate(self):
        aid = self.admin_id
        item = self.required_item
        self.destroy() 
        from src.ui.door_window import DoorAccessWindow
        DoorAccessWindow(self.parent, aid, item)

    def update_loop(self):
        if not self.winfo_exists(): return

        if self.state in ["SUCCESS", "FAILED"]:
            if self.frozen_frame is not None:
                self.render_frame(self.frozen_frame)
            self.after(30, self.update_loop)
            return

        frame = self.camera.get_frame()
        if frame is not None:
            current_display = frame.copy()

            if self.state == "DETECTING":

                elapsed_scan = time.time() - self.scan_start_time
                remaining_scan = self.MAX_SCAN_DURATION - elapsed_scan
                

                self.timer_label.config(text=f"Time Remaining: {max(0, remaining_scan):.1f}s")

                if elapsed_scan >= self.MAX_SCAN_DURATION:
                    self.state = "FAILED"
                    self.frozen_frame = current_display.copy()
                    self.status_label.config(text="ACCESS DENIED: Timeout ❌", fg="white", bg="#c0392b")
                    self.timer_label.config(text="")

                    self.db.log_access(self.admin_id, self.required_item, "DENIED", self.frozen_frame)
                    self.render_frame(self.frozen_frame)
                    self.after(30, self.update_loop)
                    return


                processed, result = self.analyzer.check_compliance(frame)
                current_display = processed

                if result == "ACCESS GRANTED":
                    if self.gotrah_timer_start is None:
                        self.gotrah_timer_start = time.time()
                    
                    elapsed_hold = time.time() - self.gotrah_timer_start
                    
                    if elapsed_hold >= self.REQUIRED_HOLD_DURATION:
                        self.state = "SUCCESS"
                        self.frozen_frame = current_display.copy()
                        self.status_label.config(text="ACCESS GRANTED ✅", fg="white", bg="#2c3e50")
                        self.timer_label.config(text="")

                        self.db.log_access(self.admin_id, self.required_item, "GRANTED", self.frozen_frame)
                        self.render_frame(self.frozen_frame)
                        self.after(30, self.update_loop)
                        return
                    else:
                        remaining_hold = self.REQUIRED_HOLD_DURATION - elapsed_hold
                        self.status_label.config(text=f"Hold Still... {remaining_hold:.1f}s", fg="#27ae60")
                else:
                    self.gotrah_timer_start = None
                    self.status_label.config(text="Scanning...", fg="#d35400")

            self.render_frame(current_display)

        self.after(30, self.update_loop)

    def render_frame(self, frame):
        try:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        except:
            pass

    def destroy(self):
        if hasattr(self, 'camera'):
            self.camera.stop()
        super().destroy()
