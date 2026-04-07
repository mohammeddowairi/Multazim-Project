# import tkinter as tk
# from tkinter import messagebox
# from src.ui.door_window import DoorAccessWindow
# from src.ui.report_window import ReportWindow

# class AdminDashboard:
#     def __init__(self, root, admin_id):
#         self.root = root
#         self.admin_id = admin_id
        
#         self.root.title("Multazim - Admin Dashboard")
#         self.root.geometry("600x500")
        
#         self.door_window = None 
#         self.report_window = None

#         # --- HEADER ---
#         header_frame = tk.Frame(root, bg="#2c3e50", height=60)
#         header_frame.pack(fill="x")
        
#         title_lbl = tk.Label(header_frame, text="Admin Dashboard", font=("Arial", 14, "bold"), bg="#2c3e50", fg="white")
#         title_lbl.pack(side="left", padx=20, pady=10)
        
#         logout_btn = tk.Button(header_frame, text="Logout", bg="#c0392b", fg="white", command=self.logout)
#         logout_btn.pack(side="right", padx=20, pady=10)

#         # --- SETTINGS ---
#         settings_frame = tk.Frame(root, pady=20)
#         settings_frame.pack()

#         tk.Label(settings_frame, text="Required Dress Code:", font=("Arial", 12)).pack(pady=5)
        
#         self.dress_var = tk.StringVar(value="Ghotra")
        
#         # --- NEW OPTIONS ---
#         dress_options = ["Ghotra", "Mask", "Helmet"]
        
#         self.combo = tk.OptionMenu(settings_frame, self.dress_var, *dress_options)
#         self.combo.config(width=20)
#         self.combo.pack(pady=5)
        
#         save_btn = tk.Button(settings_frame, text="Save Settings", command=lambda: messagebox.showinfo("Saved", "Settings Updated"))
#         save_btn.pack(pady=10)

#         # --- ACTIONS ---
#         action_frame = tk.Frame(root, pady=20)
#         action_frame.pack()

#         report_btn = tk.Button(action_frame, text="📄 VIEW REPORTS", 
#                                font=("Arial", 12), width=25,
#                                command=self.open_report_window)
#         report_btn.pack(pady=10)

#         launch_btn = tk.Button(action_frame, text="🚀 LAUNCH DOOR LIVE FEED", 
#                                bg="#27ae60", fg="white", font=("Arial", 14, "bold"),
#                                width=25, height=2, command=self.open_door_window)
#         launch_btn.pack(pady=10)

#     def open_report_window(self):
#         if self.report_window is None or not tk.Toplevel.winfo_exists(self.report_window):
#             self.report_window = ReportWindow(self.root, self.admin_id)
#         else:
#             self.report_window.lift()

#     def open_door_window(self):
#         # 1. Get the current selection (e.g., "Helmet")
#         selected_item = self.dress_var.get()
        
#         if self.door_window is None or not tk.Toplevel.winfo_exists(self.door_window):
#             # 2. Pass it to the Door Window
#             self.door_window = DoorAccessWindow(self.root, self.admin_id, selected_item)
#         else:
#             self.door_window.lift() 

#     def logout(self):
#         if messagebox.askyesno("Logout", "Are you sure?"):
#             self.root.quit()

import customtkinter as ctk
from tkinter import messagebox
from src.ui.door_window import DoorAccessWindow
from src.ui.report_window import ReportWindow

class AdminDashboard:
    def __init__(self, root, admin_id):
        self.root = root
        self.admin_id = admin_id
        
        self.root.title("Multazim - Command Center")
        self.root.geometry("1000x600")
        
        self.door_window = None
        self.report_window = None

        # --- LAYOUT GRID ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- 1. SIDEBAR (Left) ---
        self.sidebar = ctk.CTkFrame(root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Logo / Title
        ctk.CTkLabel(self.sidebar, text="MULTAZIM", font=("Roboto", 20, "bold")).grid(row=0, column=0, padx=20, pady=20)

        # Menu Buttons
        self.btn_dash = ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_reports = ctk.CTkButton(self.sidebar, text="View Reports", command=self.open_report_window)
        self.btn_reports.grid(row=2, column=0, padx=20, pady=10)

        # Logout (Bottom)
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Log Out", fg_color="#c0392b", hover_color="#e74c3c", command=self.logout)
        self.btn_logout.grid(row=5, column=0, padx=20, pady=20)

        # --- 2. MAIN CONTENT (Right) ---
        self.main_area = ctk.CTkFrame(root, corner_radius=10, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # -- SETTINGS CARD --
        self.card_settings = ctk.CTkFrame(self.main_area)
        self.card_settings.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.card_settings, text="Active Detection Mode", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.dress_var = ctk.StringVar(value="Ghotra")
        self.combo = ctk.CTkOptionMenu(self.card_settings, values=["Ghotra", "Mask", "Helmet"], variable=self.dress_var)
        self.combo.pack(pady=10)
        
        # -- ACTION CARD --
        self.card_actions = ctk.CTkFrame(self.main_area)
        self.card_actions.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(self.card_actions, text="System Controls", font=("Roboto", 16, "bold")).pack(pady=20)

        # Big Launch Button
        self.btn_launch = ctk.CTkButton(self.card_actions, text="🚀 LAUNCH LIVE GATE MONITOR", 
                                      font=("Roboto", 18, "bold"), height=80, fg_color="#27ae60", hover_color="#2ecc71",
                                      command=self.open_door_window)
        self.btn_launch.pack(padx=50, pady=20, fill="x")

        # Stats (Optional Decoration)
        self.stats_lbl = ctk.CTkLabel(self.card_actions, text="System Status: ONLINE • Database: CONNECTED", text_color="gray")
        self.stats_lbl.pack(side="bottom", pady=20)

    def open_report_window(self):
        if self.report_window is None or not self.report_window.winfo_exists():
            # Note: We keep ReportWindow as standard Tkinter or upgrade it separately
            self.report_window = ReportWindow(self.root, self.admin_id)
        else:
            self.report_window.lift()

    def open_door_window(self):
        selected = self.dress_var.get()
        if self.door_window is None or not self.door_window.winfo_exists():
            self.door_window = DoorAccessWindow(self.root, self.admin_id, selected)
        else:
            self.door_window.lift()

    def logout(self):
        if messagebox.askyesno("Logout", "Exit Admin Session?"):
            self.root.destroy()