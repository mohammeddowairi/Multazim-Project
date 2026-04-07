import customtkinter as ctk
from tkinter import messagebox
from src.logic.database_manager import DatabaseManager

class LoginWindow:
    def __init__(self, root, open_dashboard_callback):
        self.root = root
        self.open_dashboard_callback = open_dashboard_callback
        self.db = DatabaseManager()
        
        # 1. Window Config
        self.root.title("Multazim Security - Access Control")
        self.root.geometry("900x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # 2. Layout: Split Screen
        # --- LEFT SIDE: BRANDING ---
        self.left_frame = ctk.CTkFrame(root, width=400, corner_radius=0, fg_color="#1a1a1a")
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(self.left_frame, text="MULTAZIM", 
                     font=("Roboto Medium", 40), text_color="white").place(relx=0.5, rely=0.45, anchor="center")
        
        ctk.CTkLabel(self.left_frame, text="Smart Access Control System", 
                     font=("Roboto", 16), text_color="gray").place(relx=0.5, rely=0.52, anchor="center")

        # --- RIGHT SIDE: LOGIN FORM ---
        self.right_frame = ctk.CTkFrame(root, width=500, corner_radius=0, fg_color="#2b2b2b")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.login_frame = ctk.CTkFrame(self.right_frame, width=300, height=450, fg_color="transparent")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.login_frame, text="Welcome Back", font=("Roboto", 28, "bold")).pack(pady=20)

        # User Input
        self.user_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username", width=280, height=45)
        self.user_entry.pack(pady=10)

        # Pass Input
        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=280, height=45)
        self.pass_entry.pack(pady=10)

        # Login Button
        self.login_btn = ctk.CTkButton(self.login_frame, text="LOGIN", width=280, height=50, 
                                      font=("Roboto", 15, "bold"), command=self.check_login)
        self.login_btn.pack(pady=25)

        # Register Link
        self.reg_link = ctk.CTkButton(self.login_frame, text="No account? Register here", 
                                      fg_color="transparent", text_color="#3498db", 
                                      hover_color="#333333", font=("Roboto", 12),
                                      command=self.open_register_window)
        self.reg_link.pack(pady=5)

    def check_login(self):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        admin_id = self.db.validate_login(u, p)
        
        if admin_id:
            self.open_dashboard_callback(admin_id)
        else:
            messagebox.showerror("Access Denied", "Invalid Username or Password")

    def open_register_window(self):
        # Create a popup window for registration
        self.reg_win = ctk.CTkToplevel(self.root)
        self.reg_win.title("Create New Admin")
        self.reg_win.geometry("400x550")
        self.reg_win.attributes("-topmost", True) # Keep on top
        self.reg_win.grab_set() # Block main window interactions

        ctk.CTkLabel(self.reg_win, text="Register Admin", font=("Roboto", 22, "bold")).pack(pady=25)

        # Fields
        new_u = ctk.CTkEntry(self.reg_win, placeholder_text="New Username", width=300, height=40)
        new_u.pack(pady=10)

        new_e = ctk.CTkEntry(self.reg_win, placeholder_text="Email Address", width=300, height=40)
        new_e.pack(pady=10)

        new_p = ctk.CTkEntry(self.reg_win, placeholder_text="Password", show="*", width=300, height=40)
        new_p.pack(pady=10)

        new_o = ctk.CTkEntry(self.reg_win, placeholder_text="Organization Name", width=300, height=40)
        new_o.pack(pady=10)

        def handle_reg():
            user, mail, pwd, org = new_u.get(), new_e.get(), new_p.get(), new_o.get()
            
            if not user or not pwd:
                messagebox.showwarning("Incomplete", "Username and Password are required!")
                return

            if self.db.register_admin(user, mail, pwd, org):
                messagebox.showinfo("Success", f"Account created for {user}!")
                self.reg_win.destroy()
            else:
                messagebox.showerror("Failed", "Username already exists. Choose another.")

        ctk.CTkButton(self.reg_win, text="CREATE ACCOUNT", width=250, height=45, 
                     fg_color="#27ae60", hover_color="#219150", command=handle_reg).pack(pady=35)