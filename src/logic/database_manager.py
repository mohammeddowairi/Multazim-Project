import os
import sqlite3
import hashlib
import cv2  
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="multazim.db"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.db_path = os.path.join(project_root, "database", db_name)
        self.captures_path = os.path.join(project_root, "database", "captures")
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.captures_path, exist_ok=True)
        
        self.create_tables()
        self.create_default_admin()

    def get_connection(self):
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
                DetectionResult VARCHAR(50),
                ComplianceStatus VARCHAR(20), 
                ImagePath VARCHAR(255),
                FOREIGN KEY(AdminID_FK) REFERENCES Admin(AdminID)
            )
        ''')
        conn.commit()
        conn.close()

    def register_admin(self, username, email, password, org_name, dress_code):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('''
                INSERT INTO Admin (Username, Email, PasswordHash, OrganizationName, ActiveRequiredDress)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, hashed_pw, org_name, dress_code))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_access_history(self, admin_id, status_filter="All", mode_filter="All"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT L.LogID, L.Timestamp, L.DetectionResult, L.ComplianceStatus, A.OrganizationName, L.ImagePath 
        FROM AccessLog L
        JOIN Admin A ON L.AdminID_FK = A.AdminID
        WHERE L.AdminID_FK = ?
        """
        params = [admin_id]

        if status_filter != "All":
            query += " AND L.ComplianceStatus = ?"
            params.append(status_filter)
        
        if mode_filter != "All":
            query += " AND L.DetectionResult = ?"
            params.append(mode_filter)

        query += " ORDER BY L.Timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    def log_access(self, admin_id, detection_result, status, frame=None):
        """Logs an access attempt with an image capture."""
        conn = self.get_connection()
        cursor = conn.cursor()
        image_relative_path = ""

        try:
            if frame is not None:
                # Create a unique filename using timestamp
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{status}_{timestamp_str}.jpg"
                full_image_path = os.path.join(self.captures_path, file_name)
                
                # Save physical image to database/captures/
                cv2.imwrite(full_image_path, frame)
                
                # Store relative path for the UI to find it later
                image_relative_path = os.path.join("database", "captures", file_name)

            cursor.execute('''
                INSERT INTO AccessLog (AdminID_FK, Timestamp, DetectionResult, ComplianceStatus, ImagePath)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  detection_result, status, image_relative_path))
            
            conn.commit()
            print(f"✅ Access Logged to DB: {status} for Admin #{admin_id}")
        except Exception as e:
            print(f"⚠️ DB Logging Error: {e}")
        finally:
            conn.close() 
            
    def validate_login(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT AdminID FROM Admin WHERE Username=? AND PasswordHash=?", (username, hashed_pw))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def create_default_admin(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM Admin")
        if cursor.fetchone()[0] == 0:
            hashed_pw = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO Admin (Username, Email, PasswordHash, OrganizationName, ActiveRequiredDress)
                VALUES (?, ?, ?, ?, ?)
            ''', ("admin", "admin@jazanu.edu.sa", hashed_pw, "Jazan University", "Ghotra"))
            conn.commit()
        conn.close()
