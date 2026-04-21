import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from src.logic.database_manager import DatabaseManager

class LoginWindow:
    def __init__(self, root, open_dashboard_callback):
        self.root = root
        self.open_dashboard_callback = open_dashboard_callback
        self.db = DatabaseManager()
        
        # 1. Window Settings
        self.root.title("Multazim Security - Access Control")
        self.root.geometry("950x600")
        self.root.resizable(False, False)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue") 

        # --- Load and Process Logo ---
        current_path = os.path.dirname(os.path.realpath(__file__))
        logo_path = os.path.join(current_path, "../../assets/multazim logo.png")
        
        try:
            original_img = Image.open(logo_path).convert("RGBA")
            self.logo_image = ctk.CTkImage(
                light_image=original_img,
                dark_image=original_img,
                size=(380, 380) # Large, centered logo
            )
        except Exception as e:
            print(f"⚠️ Error loading logo: {e}")
            self.logo_image = None

        # --- 2. LAYOUT DESIGN (SPLIT SCREEN) ---
        
        # LEFT SIDE: Solid White Background
        self.left_frame = ctk.CTkFrame(root, width=450, corner_radius=0, fg_color="#ffffff") 
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        if self.logo_image:
            # Centered exactly in the white half
            self.logo_label = ctk.CTkLabel(self.left_frame, image=self.logo_image, text="")
            self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # RIGHT SIDE: Solid Dark Navy Background
        self.right_frame = ctk.CTkFrame(root, width=500, corner_radius=0, fg_color="#0f172a")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Container for the form to keep it centered on the navy side
        self.form_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.form_container.place(relx=0.5, rely=0.5, anchor="center")

        # TITLE: Updated to "Welcome to Multazim"
        ctk.CTkLabel(self.form_container, text="Welcome to Multazim", 
                      font=("Roboto", 32, "bold"), 
                      text_color="white").pack(pady=(0, 5))

        # SUBTITLE: Updated to (Smart dress code access system)
        ctk.CTkLabel(self.form_container, text="(Smart dress code access system)", 
                      font=("Roboto", 14), 
                      text_color="#60a5fa").pack(pady=(0, 40))

        # Input Fields
        self.user_entry = ctk.CTkEntry(self.form_container, placeholder_text="Username", 
                                       width=320, height=55, corner_radius=12,
                                       fg_color="#1e293b", border_color="#334155",
                                       text_color="white")
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self.form_container, placeholder_text="Password", 
                                       show="*", width=320, height=55, corner_radius=12,
                                       fg_color="#1e293b", border_color="#334155",
                                       text_color="white")
        self.pass_entry.pack(pady=10)

        # Login Button
        self.login_btn = ctk.CTkButton(self.form_container, text="LOGIN", 
                                        width=320, height=60, corner_radius=12, 
                                        font=("Roboto", 16, "bold"),
                                        fg_color="#2563eb", hover_color="#1d4ed8",
                                        command=self.check_login)
        self.login_btn.pack(pady=40)

        self.reg_link = ctk.CTkButton(self.form_container, text="Create a new Account", 
                                       fg_color="transparent", text_color="#60a5fa", 
                                       hover_color="#1e293b", font=("Roboto", 13, "underline"),
                                       command=self.open_register_window)
        self.reg_link.pack()

    # --- Logical Functions ---
    def check_login(self):
        u, p = self.user_entry.get(), self.pass_entry.get()
        if not u or not p:
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        admin_id = self.db.validate_login(u, p)
        if admin_id:
            self.open_dashboard_callback(admin_id)
        else:
            messagebox.showerror("Access Denied", "Invalid Username or Password")

    def open_register_window(self):
        self.reg_win = ctk.CTkToplevel(self.root)
        self.reg_win.title("Create New Admin")
        self.reg_win.geometry("450x650") # Increased height for the new field
        self.reg_win.attributes("-topmost", True)
        self.reg_win.grab_set()
        
        ctk.CTkLabel(self.reg_win, text="Register Admin", font=("Roboto", 22, "bold")).pack(pady=25)
        
        new_u = ctk.CTkEntry(self.reg_win, placeholder_text="New Username", width=320, height=45)
        new_u.pack(pady=10)
        
        new_e = ctk.CTkEntry(self.reg_win, placeholder_text="Email Address", width=320, height=45)
        new_e.pack(pady=10)
        
        new_p = ctk.CTkEntry(self.reg_win, placeholder_text="Password", show="*", width=320, height=45)
        new_p.pack(pady=10)
        
        new_o = ctk.CTkEntry(self.reg_win, placeholder_text="Organization Name", width=320, height=45)
        new_o.pack(pady=10)

        # --- NEW DRESS CODE SELECTION ---
        ctk.CTkLabel(self.reg_win, text="Default Required Attire:", font=("Roboto", 14)).pack(pady=(10, 5))
        
        # Variable to hold the selection
        dress_choice = ctk.StringVar(value="Ghotra") 
        dress_menu = ctk.CTkOptionMenu(self.reg_win, values=["Ghotra", "Mask", "Helmet"], 
                                      variable=dress_choice, width=320, height=40,
                                      fg_color="#1e293b", button_color="#2563eb")
        dress_menu.pack(pady=10)
        
        def handle_reg():
            user = new_u.get()
            mail = new_e.get()
            pwd = new_p.get()
            org = new_o.get()
            dress = dress_choice.get() # Get the selected value

            if not user or not pwd:
                messagebox.showwarning("Incomplete", "Username and Password are required!")
                return
            
            # Update this call to include the 'dress' parameter
            if self.db.register_admin(user, mail, pwd, org, dress):
                messagebox.showinfo("Success", f"Account created for {user}!")
                self.reg_win.destroy()
            else:
                messagebox.showerror("Failed", "Username already exists.")
                
        ctk.CTkButton(self.reg_win, text="CREATE ACCOUNT", width=250, height=50, 
                      fg_color="#27ae60", hover_color="#219150", font=("Roboto", 16, "bold"),
                      command=handle_reg).pack(pady=35)
