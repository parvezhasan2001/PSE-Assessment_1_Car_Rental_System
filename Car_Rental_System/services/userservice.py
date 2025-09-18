from contextlib import closing
from config.database import DatabaseConnection
from utils.auth import hash_password, verify_password
from utils.validators import validate_email, validate_password

class UserService:
    def __init__(self, db: DatabaseConnection | None = None):
        self.db = db or DatabaseConnection()

    def register_user(self, name, email, password, role="customer"):
        # Basic validation
        if not validate_email(email):
            return {"success": False, "message": "Invalid email format"}
        if not validate_password(password):
            return {"success": False, "message": "Password must be at least 8 characters long"}

        # Normalize role and restrict to allowed values
        role = (role or "customer").strip().lower()
        if role not in ("admin", "customer"):
            role = "customer"

        # Properly acquire and close the connection/cursor
        with closing(self.db.get_connection()) as conn:
            if not conn or (hasattr(conn, "is_connected") and not conn.is_connected()):
                return {"success": False, "message": "Database connection failed"}
            with closing(conn.cursor(dictionary=True)) as cursor:
                # Uniqueness check
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return {"success": False, "message": "Email already registered with this user"}

                # Hash + insert
                hashed_pw = hash_password(password)
                cursor.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed_pw, role)
                )
                conn.commit()

                return {"success": True, "message": f"User {role} registered successfully"}

    def login_user(self, email, password):
        with closing(self.db.get_connection()) as conn:
            if not conn or (hasattr(conn, "is_connected") and not conn.is_connected()):
                return {"success": False, "message": "Database connection failed"}
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if not user:
                    return {"success": False, "message": "User not found"}

                if not verify_password(password, user["password"]):
                    return {"success": False, "message": "Invalid password"}

                role = user.get("role", "customer")
                return {
                    "success": True,
                    "message": "Admin login successful" if role == "admin" else "Customer login successful",
                    "role": role,
                    "user": user
                }

    def list_customers(self, search: str | None = None, limit: int = 200, offset: int = 0):
        where = ["role = 'customer'"]
        params: list = []
        if search:
            where.append("(name LIKE %s OR email LIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])

        sql = f"""
            SELECT user_id, name, email, role, created_at
            FROM users
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([int(limit), int(offset)])

        with closing(self.db.get_connection()) as conn:
            if not conn or (hasattr(conn, "is_connected") and not conn.is_connected()):
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() or []
        return {"success": True, "customers": rows}

    def delete_user(self, admin_role: str, user_id: int):
        if admin_role != "admin":
            return {"success": False, "message": "Forbidden: admin only"}

        with closing(self.db.get_connection()) as conn:
            if not conn or (hasattr(conn, "is_connected") and not conn.is_connected()):
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute("SELECT role FROM users WHERE user_id=%s", (user_id,))
                row = cur.fetchone()
                if not row:
                    return {"success": False, "message": "User not found"}
                if row["role"] == "admin":
                    return {"success": False, "message": "Refusing to delete an admin"}

                cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
                conn.commit()
                if cur.rowcount == 0:
                    return {"success": False, "message": "User not found / not deleted"}
                return {"success": True, "message": "User deleted"}
