import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

try:
    from src.logic.database_manager import DatabaseManager
except ImportError:
    class DatabaseManager:
        def validate_login(self, u, p): return True 
        def register_admin(self, *args): return True

class LoginWindow:
    def __init__(self, root, open_dashboard_callback):
        self.root = root
        self.open_dashboard_callback = open_dashboard_callback
        self.db = DatabaseManager()
        

        self.root.title("MULTAZIM - Smart Dress Code Access Control System")
        self.root.geometry("1150x750")
        self.root.resizable(False, False)
        
        self.root.configure(fg_color="#081021") 
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue") 

        current_path = os.path.dirname(os.path.realpath(__file__))
        bg_path = os.path.join(current_path, "../../assets/background.png")
        
        try:
            bg_image_pil = Image.open(bg_path)
            self.bg_image = ctk.CTkImage(
                light_image=bg_image_pil,
                dark_image=bg_image_pil,
                size=(1150, 750) 
            )
        except Exception as e:
            print(f"⚠️ Error loading background image: {e}")
            self.bg_image = None

        self.bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)


        
        self.form_container = ctk.CTkFrame(
            self.root, 
            fg_color="#03050a",        
            bg_color="transparent",    # Inherits the #081021 navy blue to hide edges completely!
            corner_radius=40,          
            border_width=0
        ) 
        
        self.form_container.place(relx=0.72, rely=0.5, anchor="center")


        self.inner_form = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.inner_form.pack(padx=50, pady=50)


        ctk.CTkLabel(self.inner_form, text="Welcome to Multazim", 
                      font=("Roboto", 32, "bold"), 
                      text_color="white").pack(pady=(0, 5))

        ctk.CTkLabel(self.inner_form, text="(Smart dress code access system)", 
                      font=("Roboto", 14), 
                      text_color="#60a5fa").pack(pady=(0, 40))


        entry_style = {
            "width": 320, "height": 55, "corner_radius": 12,
            "fg_color": "#0f172a", "border_color": "#1e293b", "border_width": 1,
            "text_color": "white", "font": ("Roboto", 14)
        }

        self.user_entry = ctk.CTkEntry(self.inner_form, placeholder_text="Username", **entry_style)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self.inner_form, placeholder_text="Password", show="*", **entry_style)
        self.pass_entry.pack(pady=10)


        self.login_btn = ctk.CTkButton(self.inner_form, text="LOGIN", 
                                        width=320, height=60, corner_radius=12, 
                                        font=("Roboto", 16, "bold"),
                                        fg_color="#2563eb", hover_color="#1d4ed8",
                                        command=self.check_login)
        self.login_btn.pack(pady=(30, 20))


        self.reg_link = ctk.CTkButton(self.inner_form, text="Create a new Account", 
                                       fg_color="transparent", text_color="#60a5fa", 
                                       hover_color="#03050a", font=("Roboto", 13, "underline"),
                                       command=self.open_register_window)
        self.reg_link.pack()

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
        self.reg_win.geometry("480x650") 
        self.reg_win.attributes("-topmost", True)
        self.reg_win.grab_set()
        self.reg_win.configure(fg_color="#081021")
        
        ctk.CTkLabel(self.reg_win, text="Register Admin", font=("Roboto", 24, "bold"), text_color="white").pack(pady=30)
        
        input_style = {"width": 340, "height": 50, "corner_radius": 12, "fg_color": "#0f172a", "border_width": 0}
        
        new_u = ctk.CTkEntry(self.reg_win, placeholder_text="New Username", **input_style)
        new_u.pack(pady=10)
        new_e = ctk.CTkEntry(self.reg_win, placeholder_text="Email Address", **input_style)
        new_e.pack(pady=10)
        new_p = ctk.CTkEntry(self.reg_win, placeholder_text="Password", show="*", **input_style)
        new_p.pack(pady=10)
        new_o = ctk.CTkEntry(self.reg_win, placeholder_text="Organization Name", **input_style)
        new_o.pack(pady=10)

        dress_choice = ctk.StringVar(value="Ghotra") 
        dress_menu = ctk.CTkOptionMenu(self.reg_win, values=["Ghotra", "Mask", "Helmet"], 
                                       variable=dress_choice, width=340, height=45, corner_radius=12)
        dress_menu.pack(pady=15)
        
        def handle_reg():
            if self.db.register_admin(new_u.get(), new_e.get(), new_p.get(), new_o.get(), dress_choice.get()):
                messagebox.showinfo("Success", f"Account created for {new_u.get()}!")
                self.reg_win.destroy()
            else:
                messagebox.showerror("Failed", "Username already exists.")

        ctk.CTkButton(self.reg_win, text="CREATE ACCOUNT", width=280, height=55, 
                       corner_radius=12, fg_color="#27ae60", font=("Roboto", 16, "bold"), 
                       command=handle_reg).pack(pady=40)

if __name__ == "__main__":
    app = ctk.CTk()
    login = LoginWindow(app, lambda id: print(f"Logged in: {id}"))
    app.mainloop()
