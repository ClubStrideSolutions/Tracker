import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import bcrypt

class Database:
    def __init__(self, db_path: str = "data/intern_tracker.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE,
                school TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Core Intern', 'Lead Intern', 'Admin')),
                start_date DATE NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Pending Approval', 'Active', 'Inactive')) DEFAULT 'Pending Approval',
                auth_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Hours table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                total_hours REAL NOT NULL,
                description TEXT NOT NULL,
                approved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Deliverables table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliverables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                links TEXT,
                proof_links TEXT,
                status TEXT NOT NULL CHECK(status IN ('Pending', 'Approved', 'Needs Revision', 'Rejected')) DEFAULT 'Pending',
                admin_comments TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

        # Create admin account if not exists
        self.create_default_admin()

    def create_default_admin(self):
        """Create default admin account"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE email = 'admin@clubstride.org'")
        if cursor.fetchone() is None:
            password_hash = bcrypt.hashpw("admin123456".encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (name, email, username, school, role, start_date, status, auth_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Admin", "admin@clubstride.org", "admin123", "N/A", "Admin",
                  datetime.now().date(), "Active", password_hash.decode('utf-8')))
            conn.commit()

        conn.close()

    # User Management
    def create_account_request(self, name: str, email: str, school: str, role: str) -> bool:
        """Create a new account request (pending approval)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, school, role, start_date, status)
                VALUES (?, ?, ?, ?, ?, 'Pending Approval')
            ''', (name, email, school, role, datetime.now().date()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending account requests"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, school, role, start_date, created_at
            FROM users WHERE status = 'Pending Approval'
            ORDER BY created_at DESC
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def approve_account(self, user_id: int, username: str, password: str) -> bool:
        """Approve account and set credentials"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                UPDATE users
                SET status = 'Active', username = ?, auth_hash = ?
                WHERE id = ?
            ''', (username, password_hash.decode('utf-8'), user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def reject_account(self, user_id: int) -> bool:
        """Reject and delete account request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ? AND status = 'Pending Approval'", (user_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, username, role, status, auth_hash
            FROM users WHERE username = ? AND status = 'Active'
        ''', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['auth_hash'].encode('utf-8')):
            return dict(user)
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all active users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, username, school, role, start_date, status
            FROM users WHERE status = 'Active' AND role != 'Admin'
            ORDER BY name
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def toggle_user_status(self, user_id: int, new_status: str) -> bool:
        """Activate or deactivate user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
        conn.commit()
        conn.close()
        return True

    # Hours Management
    def log_hours(self, user_id: int, date: str, start_time: str, end_time: str,
                  total_hours: float, description: str) -> bool:
        """Log work hours"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hours (user_id, date, start_time, end_time, total_hours, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, date, start_time, end_time, total_hours, description))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging hours: {e}")
            return False

    def get_user_hours(self, user_id: int, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get hours for a specific user with optional date range"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM hours WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, start_time DESC"

        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_all_hours(self) -> List[Dict[str, Any]]:
        """Get all hours entries with user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT h.*, u.name as user_name, u.email as user_email
            FROM hours h
            JOIN users u ON h.user_id = u.id
            ORDER BY h.date DESC, h.start_time DESC
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def approve_hours(self, hour_id: int, approved: bool = True) -> bool:
        """Approve or reject hours entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE hours SET approved = ? WHERE id = ?", (approved, hour_id))
        conn.commit()
        conn.close()
        return True

    def get_total_hours(self, user_id: int, approved_only: bool = False) -> float:
        """Get total hours for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT SUM(total_hours) as total FROM hours WHERE user_id = ?"
        if approved_only:
            query += " AND approved = 1"

        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result['total'] if result['total'] else 0.0

    # Deliverables Management
    def submit_deliverable(self, user_id: int, deliv_type: str, description: str,
                          links: str = "", proof_links: str = "") -> bool:
        """Submit a new deliverable"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO deliverables (user_id, type, description, links, proof_links)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, deliv_type, description, links, proof_links))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error submitting deliverable: {e}")
            return False

    def get_user_deliverables(self, user_id: int) -> List[Dict[str, Any]]:
        """Get deliverables for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM deliverables
            WHERE user_id = ?
            ORDER BY submitted_at DESC
        ''', (user_id,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_all_deliverables(self) -> List[Dict[str, Any]]:
        """Get all deliverables with user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.*, u.name as user_name, u.email as user_email
            FROM deliverables d
            JOIN users u ON d.user_id = u.id
            ORDER BY d.submitted_at DESC
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def update_deliverable_status(self, deliv_id: int, status: str,
                                  admin_comments: str = "") -> bool:
        """Update deliverable status and add admin comments"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE deliverables
            SET status = ?, admin_comments = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, admin_comments, deliv_id))
        conn.commit()
        conn.close()
        return True

    def get_pending_deliverables(self) -> List[Dict[str, Any]]:
        """Get all pending deliverables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.*, u.name as user_name, u.email as user_email
            FROM deliverables d
            JOIN users u ON d.user_id = u.id
            WHERE d.status = 'Pending'
            ORDER BY d.submitted_at ASC
        ''')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results