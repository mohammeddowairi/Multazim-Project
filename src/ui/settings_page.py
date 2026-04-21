import customtkinter as ctk
import os

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, admin_id, db_manager, dress_var):
        super().__init__(parent, fg_color="transparent")
        self.db = db_manager
        self.admin_id = admin_id

        # --- Fetch Data ---
        conn = self.db.get_connection()
        user_data = conn.execute("SELECT Username, Email, OrganizationName FROM Admin WHERE AdminID=?", (admin_id,)).fetchone()
        
        # Real-time log count
        total_logs = conn.execute("SELECT COUNT(*) FROM AccessLog WHERE AdminID_FK=?", (admin_id,)).fetchone()[0]
        conn.close()

        # Page Header
        ctk.CTkLabel(self, text="Admin Settings", font=("Roboto", 32, "bold"), text_color="white").pack(anchor="w", padx=40, pady=(40, 5))
        ctk.CTkLabel(self, text="Configure your profile and system detection requirements.", 
                     font=("Roboto", 14), text_color="#94a3b8").pack(anchor="w", padx=40, pady=(0, 25))

        # --- SCROLLABLE CONTAINER (In case the screen is small) ---
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#1f2c41")
        self.container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        # 1. ACCOUNT PROFILE (Row 1 - Full Width)
        self.profile_card = self.create_section_card(self.container, "👤 Account Profile")
        
        info_inner = ctk.CTkFrame(self.profile_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=20, pady=(0, 20))
        
        self.add_detail(info_inner, "Username", user_data[0] if user_data else "N/A")
        self.add_detail(info_inner, "Email Address", user_data[1] if user_data else "N/A")
        self.add_detail(info_inner, "Organization", user_data[2] if user_data else "N/A")

        # 2. DETECTION CONFIGURATION (Row 2 - Full Width)
        self.config_card = self.create_section_card(self.container, "⚙️ Detection Configuration")
        
        config_inner = ctk.CTkFrame(self.config_card, fg_color="transparent")
        config_inner.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(config_inner, text="Select the active dress code requirement for the gate monitor:", 
                     font=("Roboto", 13), text_color="#94a3b8").pack(anchor="w", pady=(0, 10))
        
        self.combo = ctk.CTkOptionMenu(config_inner, values=["Ghotra", "Mask", "Helmet"], 
                                       variable=dress_var, width=300, height=40, 
                                       fg_color="#1a253a", button_color="#3498db",
                                       command=self.save_settings)
        self.combo.pack(anchor="w")

        # 3. SYSTEM STATISTICS (Row 3 - Full Width)
        self.stats_card = self.create_section_card(self.container, "📊 System Statistics")
        
        stats_inner = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        stats_inner.pack(fill="x", padx=20, pady=(0, 25))
        
        # Displaying the total logs in a big, readable way
        log_box = ctk.CTkFrame(stats_inner, fg_color="#1a253a", corner_radius=10, height=80)
        log_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(log_box, text=str(total_logs), font=("Roboto", 28, "bold"), text_color="#2ecc71").pack(pady=(10, 0))
        ctk.CTkLabel(log_box, text="TOTAL CAPTURED LOGS", font=("Roboto", 11, "bold"), text_color="#64748b").pack(pady=(0, 10))

        status_box = ctk.CTkFrame(stats_inner, fg_color="#1a253a", corner_radius=10, height=80)
        status_box.pack(side="left", fill="x", expand=True, padx=10)
        
        ctk.CTkLabel(status_box, text="ONLINE", font=("Roboto", 24, "bold"), text_color="#3498db").pack(pady=(15, 0))
        ctk.CTkLabel(status_box, text="SYSTEM STATUS", font=("Roboto", 11, "bold"), text_color="#64748b").pack(pady=(0, 15))

    def create_section_card(self, parent, title):
        """Creates a full-width card with a blue title header"""
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="#1f2c41")
        card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(card, text=title, font=("Roboto", 18, "bold"), text_color="#3498db").pack(anchor="w", padx=20, pady=20)
        return card

    def add_detail(self, parent, label, value):
        """Adds a clean row of information"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=f"{label}:", font=("Roboto", 13, "bold"), text_color="#64748b", width=120, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=value, font=("Roboto", 14), text_color="white").pack(side="left")

    def save_settings(self, choice):
        """Auto-save to database"""
        try:
            conn = self.db.get_connection()
            conn.execute("UPDATE Admin SET ActiveRequiredDress = ? WHERE AdminID = ?", (choice, self.admin_id))
            conn.commit()
            conn.close()
            print(f"✅ Auto-saved: {choice}")
        except Exception as e:
            print(f"⚠️ Save Error: {e}")