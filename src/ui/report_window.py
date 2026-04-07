import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from src.logic.database_manager import DatabaseManager

class ReportWindow(tk.Toplevel):
    def __init__(self, parent, admin_id):
        super().__init__(parent)
        self.admin_id = admin_id
        self.db = DatabaseManager() # This now uses the absolute path
        
        self.title("Multazim - Access Reports")
        self.geometry("850x550")
        self.configure(bg="#f5f6fa")

        # --- HEADER ---
        lbl = tk.Label(self, text="Detailed Access History", font=("Roboto", 18, "bold"), 
                       bg="#f5f6fa", fg="#2f3640", pady=20)
        lbl.pack()

        # --- TABLE (Treeview) ---
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        columns = ("Timestamp", "Detection", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        self.tree.heading("Timestamp", text="Date & Time")
        self.tree.heading("Detection", text="Detection Mode")
        self.tree.heading("Status", text="Result")
        
        self.tree.column("Timestamp", width=250, anchor="center")
        self.tree.column("Detection", width=200, anchor="center")
        self.tree.column("Status", width=150, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=30, pady=10)

        # --- BUTTONS ---
        btn_frame = tk.Frame(self, bg="#f5f6fa")
        btn_frame.pack(pady=25)

        tk.Button(btn_frame, text="🔄 REFRESH", width=15, bg="#3498db", fg="white", 
                  font=("Arial", 10, "bold"), command=self.load_data).pack(side="left", padx=10)

        tk.Button(btn_frame, text="💾 EXPORT CSV", width=15, bg="#27ae60", fg="white", 
                  font=("Arial", 10, "bold"), command=self.export_csv).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="CLOSE", width=15, command=self.destroy).pack(side="left", padx=10)

        # LOAD DATA IMMEDIATELY
        self.load_data()

    def load_data(self):
        """Clears table and reloads from DB based on AdminID"""
        # 1. Clear current table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Fetch new data
        try:
            logs = self.db.get_logs_for_admin(self.admin_id)
            if not logs:
                print("Notice: No logs found for this admin.")
            
            for log in logs:
                self.tree.insert("", "end", values=log)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load data: {e}")

    def export_csv(self):
        logs = self.db.get_logs_for_admin(self.admin_id)
        if not logs:
            messagebox.showwarning("Empty", "Nothing to export.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Item", "Status"])
                writer.writerows(logs)
            messagebox.showinfo("Success", "Report Exported!")