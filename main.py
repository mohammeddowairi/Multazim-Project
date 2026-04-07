import customtkinter as ctk
from src.ui.login_window import LoginWindow
from src.ui.admin_dashboard import AdminDashboard

def main():
    # Setup the Root Window using CustomTkinter
    root = ctk.CTk()
    
    # Callback to switch screens
    def show_dashboard(admin_id):
        # Clear login screen
        for widget in root.winfo_children():
            widget.destroy()
            
        # Initialize Dashboard
        app = AdminDashboard(root, admin_id)

    # Start with Login Screen
    app = LoginWindow(root, show_dashboard)
    
    root.mainloop()

if __name__ == "__main__":
    main()