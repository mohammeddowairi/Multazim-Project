import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from src.ui.door_window import DoorAccessWindow
from src.ui.report_window import ReportPage
from src.ui.settings_page import SettingsPage
from src.logic.database_manager import DatabaseManager

class AdminDashboard:
    def __init__(self, root, admin_id):
        self.root = root
        self.admin_id = admin_id
        self.db = DatabaseManager()
        
        # --- THEME COLORS ---
        self.sidebar_white = "#ffffff"
        self.navy_dark = "#1a253a"
        self.bg_main = "#0f172a"
        self.accent_blue = "#3498db"
        self.border_gray = "#e2e8f0"
        
        self.root.title("Multazim Security - Command Center")
        self.root.geometry("1150x750")
        ctk.set_appearance_mode("Dark")

        # Sync dress code from DB
        saved_dress = self.get_saved_dress_code()
        self.dress_var = ctk.StringVar(value=saved_dress)

        # --- LOAD LOGO ---
        current_path = os.path.dirname(os.path.realpath(__file__))
        logo_path = os.path.join(current_path, "../../assets/multazim logo.png")
        
        try:
            logo_img = Image.open(logo_path)
            self.sidebar_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(180, 180))
        except:
            self.sidebar_logo = None

        # --- LAYOUT ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(root, width=260, corner_radius=0, fg_color=self.sidebar_white)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        if self.sidebar_logo:
            ctk.CTkLabel(self.sidebar, image=self.sidebar_logo, text="").pack(pady=(40, 20))

        self.btn_live = self.add_nav_button("📹 Live Monitor", self.show_live_view)
        self.btn_reports = self.add_nav_button("📊 View Reports", self.show_reports_view)
        self.btn_settings = self.add_nav_button("⚙️ Profile Settings", self.show_settings_view)

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Log Out", fg_color="#c0392b", 
                                       hover_color="#e74c3c", height=45, corner_radius=12,
                                       text_color="white", font=("Roboto", 14, "bold"),
                                       command=self.logout)
        self.btn_logout.pack(side="bottom", padx=20, pady=30, fill="x")

        self.main_container = ctk.CTkFrame(root, corner_radius=0, fg_color=self.bg_main)
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.show_live_view()

    def get_saved_dress_code(self):
        try:
            conn = self.db.get_connection()
            res = conn.execute("SELECT ActiveRequiredDress FROM Admin WHERE AdminID=?", (self.admin_id,)).fetchone()
            conn.close()
            return res[0] if res else "Ghotra"
        except: return "Ghotra"

    def add_nav_button(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color=self.navy_dark, 
                            border_width=1, border_color=self.border_gray, hover_color="#f8fafc",
                            anchor="w", height=50, corner_radius=15, font=("Roboto", 14, "bold"), command=command)
        btn.pack(fill="x", padx=20, pady=8)
        return btn

    def update_btn_styles(self, active_btn):
        for b in [self.btn_live, self.btn_reports, self.btn_settings]:
            b.configure(fg_color="transparent", text_color=self.navy_dark, border_width=1, border_color=self.border_gray)
        active_btn.configure(fg_color=self.accent_blue, text_color="white", border_width=0)

    def clear_main_area(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def show_live_view(self):
        self.clear_main_area()
        self.update_btn_styles(self.btn_live)
        ctk.CTkLabel(self.main_container, text=f"Welcome back, Admin #{self.admin_id}", 
                     font=("Roboto", 14), text_color="#94a3b8").pack(anchor="w", padx=40, pady=(40, 0))
        card = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="#1f2c41")
        card.pack(expand=True, fill="both", padx=40, pady=40)
        ctk.CTkLabel(card, text="Gate Operations", font=("Roboto", 24, "bold"), text_color="white").pack(pady=40)
        ctk.CTkButton(card, text="🚀 LAUNCH LIVE GATE MONITOR", font=("Roboto", 22, "bold"), height=100, width=500, 
                       fg_color="#27ae60", hover_color="#2ecc71",
                       command=lambda: DoorAccessWindow(self.root, self.admin_id, self.dress_var.get())).pack(pady=20)
        ctk.CTkLabel(card, text="SYSTEM STATUS: ONLINE • DB: CONNECTED", text_color="#2ecc71", font=("Roboto", 12, "bold")).pack(side="bottom", pady=20)

    def show_reports_view(self):
        self.clear_main_area()
        self.update_btn_styles(self.btn_reports)
        
        # We create a NEW instance of ReportPage every time the button is clicked.
        # This forces the __init__ and apply_filters() to run again, fetching fresh data.
        self.current_report_page = ReportPage(self.main_container, self.admin_id)
        self.current_report_page.pack(expand=True, fill="both")

    def show_settings_view(self):
        self.clear_main_area()
        self.update_btn_styles(self.btn_settings)
        SettingsPage(self.main_container, self.admin_id, self.db, self.dress_var).pack(expand=True, fill="both")

    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to end the session?"): self.root.destroy()
