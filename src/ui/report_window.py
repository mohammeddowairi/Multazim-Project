import csv
import os
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import customtkinter as ctk
from src.logic.database_manager import DatabaseManager

class ReportPage(ctk.CTkFrame):
    def __init__(self, parent, admin_id):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        self.admin_id = admin_id

        # --- Main Navy Card ---
        self.card = ctk.CTkFrame(self, corner_radius=15, fg_color="#1f2c41")
        self.card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.card, text="Detailed Access History", 
                      font=("Roboto", 24, "bold"), text_color="white").pack(pady=(20, 5))
        
        ctk.CTkLabel(self.card, text="💡 Click [ View ] to see the captured evidence", 
                      font=("Roboto", 12), text_color="#94a3b8").pack(pady=(0, 10))

        # --- FILTER SECTION ---
        self.filter_frame = ctk.CTkFrame(self.card, fg_color="#1a253a", corner_radius=10)
        self.filter_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.filter_frame, text="🔍 QUICK FILTERS :", 
                     font=("Roboto", 13, "bold"), 
                     text_color= "#3498db").pack(side="left", padx=(20, 10), pady=12)

        ctk.CTkLabel(self.filter_frame, text="|", text_color="#334155").pack(side="left", padx=5)

        # Status Filter
        ctk.CTkLabel(self.filter_frame, text="Status", font=("Roboto", 12)).pack(side="left", padx=(15, 5))
        self.status_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(self.filter_frame, values=["All", "GRANTED", "DENIED"],
                           variable=self.status_var, command=self.apply_filters,
                           width=110, height=32, fg_color="#1f2c41", button_color="#3498db").pack(side="left", padx=5)

        # Type Filter
        ctk.CTkLabel(self.filter_frame, text="Type", font=("Roboto", 12)).pack(side="left", padx=(15, 5))
        self.mode_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(self.filter_frame, values=["All", "Ghotra", "Mask", "Helmet"],
                           variable=self.mode_var, command=self.apply_filters,
                           width=110, height=32, fg_color="#1f2c41", button_color="#3498db").pack(side="left", padx=5)

        # Export CSV Button
        ctk.CTkButton(self.filter_frame, text="Export CSV", width=90, height=32, 
                      fg_color="#27ae60", hover_color="#1e8449",
                      font=("Roboto", 12, "bold"),
                      command=self.export_to_csv).pack(side="right", padx=20)

        # Reset Button
        ctk.CTkButton(self.filter_frame, text="Reset All", width=90, height=32, fg_color="#e74c3c", 
                      hover_color="#c0392b", font=("Roboto", 12, "bold"),
                      command=self.reset_filters).pack(side="right", padx=0)

        # --- TABLE ---
        self.setup_table()
        
        # Click listener for the [ View ] link
        self.tree.bind("<ButtonRelease-1>", self.on_table_click)
        
        self.apply_filters()

    def setup_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a253a", foreground="white", 
                        fieldbackground="#1a253a", rowheight=35, font=("Roboto", 11))
        style.map("Treeview", background=[('selected', '#3498db')])

        columns = ("id", "timestamp", "mode", "org", "result", "image")
        self.tree = ttk.Treeview(self.card, columns=columns, show="headings")
        
        self.tree.heading("id", text="Log ID")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("mode", text="Mode")
        self.tree.heading("org", text="Organization")
        self.tree.heading("result", text="Result")
        self.tree.heading("image", text="Image") 

        for col, w in zip(columns, [60, 180, 100, 150, 100, 100]):
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def on_table_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#6": 
                item = self.tree.identify_row(event.y)
                if item:
                    log_id = item
                    self.open_image_popup(log_id)

    def open_image_popup(self, log_id):
        conn = self.db.get_connection()
        res = conn.execute("SELECT ImagePath FROM AccessLog WHERE LogID=?", (log_id,)).fetchone()
        conn.close()

        if res and res[0]:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
            full_path = os.path.join(project_root, res[0])

            if os.path.exists(full_path):
                pop = ctk.CTkToplevel(self)
                pop.title(f"Capture Detail - Log #{log_id}")
                pop.geometry("620x540")
                pop.attributes("-topmost", True)

                img = Image.open(full_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(580, 420))
                ctk.CTkLabel(pop, image=ctk_img, text="").pack(pady=20)
                ctk.CTkButton(pop, text="Close", command=pop.destroy).pack(pady=10)
            else:
                messagebox.showerror("Error", "Image file missing.")

    def apply_filters(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        records = self.db.get_access_history(self.admin_id, self.status_var.get(), self.mode_var.get())
        total_count = len(records)
        
        for i, rec in enumerate(records):
            display_id = total_count - i
            view_btn = "[ View ]"
            display_values = (display_id, rec[1], rec[2], rec[4], rec[3], view_btn)
            
            self.tree.insert("", "end", iid=rec[0], values=display_values)
            
            tag = "granted" if rec[3] == "GRANTED" else "denied"
            self.tree.tag_configure("granted", foreground="#2ecc71")
            self.tree.tag_configure("denied", foreground="#e74c3c")
            self.tree.item(rec[0], tags=(tag,))
            
    def reset_filters(self):
        self.status_var.set("All")
        self.mode_var.set("All")
        self.apply_filters()

    def export_to_csv(self):
        records = self.db.get_access_history(self.admin_id, self.status_var.get(), self.mode_var.get())
        
        if not records:
            messagebox.showwarning("No Data", "There are no records to export with the current filters.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Access History"
        )

        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Log ID", "Timestamp", "Mode", "Organization", "Result"])
                    for rec in records:
                        # rec order based on get_access_history: ID, Time, Mode, Result, Org
                        writer.writerow([rec[0], rec[1], rec[2], rec[4], rec[3]])
                
                messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred while saving: {e}")
