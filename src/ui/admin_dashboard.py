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
        
        # --- THEME COLORS (Updated for Dark Security Theme) ---
        self.bg_main = "#03050a"       # خلفية رئيسية داكنة جداً لتتماشى مع الهوية
        self.accent_blue = "#2563eb"   # أزرق ساطع للأزرار النشطة
        self.text_light = "#f8fafc"    # نص أبيض/رمادي فاتح
        self.text_muted = "#94a3b8"    # نص رمادي خافت للتفاصيل
        self.border_color = "#1e293b"  # لون الحدود
        self.sidebar_bg = "#081021"    # لون افتراضي للشريط الجانبي (سيتم تحديثه من الشعار)
        
        self.root.title("MULTAZIM - Smart Dress Code Access Control System")
        self.root.geometry("1150x750")
        ctk.set_appearance_mode("Dark")

        # Sync dress code from DB
        saved_dress = self.get_saved_dress_code()
        self.dress_var = ctk.StringVar(value=saved_dress)

        # --- LOAD LOGO & EXTRACT BACKGROUND COLOR ---
        current_path = os.path.dirname(os.path.realpath(__file__))
        logo_path = os.path.join(current_path, "../../assets/multazim logo.png")
        
        try:
            original_img = Image.open(logo_path).convert("RGBA")
            
            # سحب لون الخلفية من الزاوية العلوية اليسرى لدمج الشعار في الشريط الجانبي
            r, g, b, a = original_img.getpixel((0, 0))
            self.sidebar_bg = f"#{r:02x}{g:02x}{b:02x}"
            
            self.sidebar_logo = ctk.CTkImage(light_image=original_img, dark_image=original_img, size=(200, 200))
        except Exception as e:
            print(f"⚠️ Error loading logo: {e}")
            self.sidebar_logo = None

        # --- LAYOUT ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # الشريط الجانبي (أصبح الآن داكناً بنفس لون خلفية الشعار)
        self.sidebar = ctk.CTkFrame(root, width=260, corner_radius=0, fg_color=self.sidebar_bg)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        if self.sidebar_logo:
            self.logo_label = ctk.CTkLabel(self.sidebar, image=self.sidebar_logo, text="")
            self.logo_label.pack(pady=(30, 20))

        # أزرار التنقل
        self.btn_live = self.add_nav_button("📹 Live Monitor", self.show_live_view)
        self.btn_reports = self.add_nav_button("📊 View Reports", self.show_reports_view)
        self.btn_settings = self.add_nav_button("⚙️ Profile Settings", self.show_settings_view)

        # زر تسجيل الخروج
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Log Out", fg_color="#b91c1c", 
                                        hover_color="#991b1b", height=45, corner_radius=8,
                                        text_color="white", font=("Roboto", 14, "bold"),
                                        command=self.logout)
        self.btn_logout.pack(side="bottom", padx=20, pady=30, fill="x")

        # الحاوية الرئيسية للمحتوى
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
        # تم تحديث ألوان الأزرار لتناسب الشريط الجانبي الداكن
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color=self.text_light, 
                            hover_color="#1e293b", anchor="w", height=50, corner_radius=8, 
                            font=("Roboto", 14, "bold"), command=command)
        btn.pack(fill="x", padx=20, pady=5)
        return btn

    def update_btn_styles(self, active_btn):
        # إعادة ضبط جميع الأزرار إلى الحالة غير النشطة
        for b in [self.btn_live, self.btn_reports, self.btn_settings]:
            b.configure(fg_color="transparent", text_color=self.text_light)
        # تمييز الزر النشط
        active_btn.configure(fg_color=self.accent_blue, text_color="white")

    def clear_main_area(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def show_live_view(self):
        self.clear_main_area()
        self.update_btn_styles(self.btn_live)
        
        ctk.CTkLabel(self.main_container, text=f"Welcome back, Admin #{self.admin_id}", 
                     font=("Roboto", 14), text_color=self.text_muted).pack(anchor="w", padx=40, pady=(40, 0))
        

        border_frame = ctk.CTkFrame(self.main_container, fg_color=self.border_color, corner_radius=22)
        border_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        card = ctk.CTkFrame(border_frame, fg_color="#0f172a", corner_radius=20)
        card.pack(expand=True, fill="both", padx=2, pady=2) # 2px gap للمسار المضيء
        
        ctk.CTkLabel(card, text="Gate Operations", font=("Roboto", 28, "bold"), text_color="white").pack(pady=(60, 40))
        
        ctk.CTkButton(card, text="🚀 LAUNCH LIVE GATE MONITOR", font=("Roboto", 22, "bold"), height=90, width=500, 
                       corner_radius=8, fg_color="#16a34a", hover_color="#15803d",
                       command=lambda: DoorAccessWindow(self.root, self.admin_id, self.dress_var.get())).pack(pady=20)
                       
        ctk.CTkLabel(card, text="🟢 SYSTEM STATUS: ONLINE • DB: CONNECTED", 
                     text_color="#4ade80", font=("Roboto", 12, "bold")).pack(side="bottom", pady=30)

    def show_reports_view(self):
        self.clear_main_area()
        self.update_btn_styles(self.btn_reports)
        
        self.current_report_page = ReportPage(self.main_container, self.admin_id)
        self.current_report_page.pack(expand=True, fill="both")

    def show_settings_view(self):
        self.clear_main_area()
        self.update_btn_styles(self.btn_settings)
        SettingsPage(self.main_container, self.admin_id, self.db, self.dress_var).pack(expand=True, fill="both")

    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to end the session?"): self.root.destroy()
