import os
import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="multazim.db"):
        # 1. Get the directory where this script lives (src/logic)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Go up two levels to the project root (MULTAZIM_PROJECT)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 3. Target the 'database' folder specifically
        self.db_path = os.path.join(project_root, "database", db_name)
        
        print(f"--- DATABASE LINKED: {self.db_path} ---")
        
        self.create_tables()
        self.create_default_admin()

    def get_connection(self):
        """Always uses the absolute path to connect."""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Admin (
                AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username VARCHAR(50) UNIQUE NOT NULL,
                Email VARCHAR(100),
                PasswordHash VARCHAR(255) NOT NULL,
                OrganizationName VARCHAR(100),
                ActiveRequiredDress VARCHAR(30) DEFAULT 'Ghotra'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AccessLog (
                LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                AdminID_FK INTEGER,
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                DetectionResult VARCHAR(20),
                ComplianceStatus VARCHAR(20),
                ImagePath VARCHAR(255),
                FOREIGN KEY(AdminID_FK) REFERENCES Admin(AdminID)
            )
        ''')
        conn.commit()
        conn.close()

    def register_admin(self, username, email, password, org_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('''
                INSERT INTO Admin (Username, Email, PasswordHash, OrganizationName)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_pw, org_name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False 
        finally:
            conn.close()

    def validate_login(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT AdminID FROM Admin WHERE Username=? AND PasswordHash=?", 
                       (username, hashed_pw))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def log_access(self, admin_id, detection_result, status, image_path=""):
        """Saves a new entry to AccessLog."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO AccessLog (AdminID_FK, Timestamp, DetectionResult, ComplianceStatus, ImagePath)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), detection_result, status, image_path))
        conn.commit()
        conn.close()

    def get_logs_for_admin(self, admin_id):
        """Fetches all access logs for the CURRENT logged-in admin."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT Timestamp, DetectionResult, ComplianceStatus 
            FROM AccessLog 
            WHERE AdminID_FK = ? 
            ORDER BY Timestamp DESC
        '''
        cursor.execute(query, (admin_id,))
        rows = cursor.fetchall()
        
        print(f"LOGS: Found {len(rows)} entries for Admin ID {admin_id}")
        conn.close()
        return rows

    def create_default_admin(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM Admin")
        if cursor.fetchone()[0] == 0:
            hashed_pw = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO Admin (Username, Email, PasswordHash, OrganizationName)
                VALUES (?, ?, ?, ?)
            ''', ("admin", "admin@jazanu.edu.sa", hashed_pw, "Jazan University"))
            conn.commit()
        conn.close()