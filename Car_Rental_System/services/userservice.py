from ..config.database import get_connection
from ..utils.auth import hash_password, verify_password
from ..utils.validators import validate_email, validate_password

class UserService:

    def register_user(name, email, password, role="customer"):
        if not validate_email(email):
            return {"success": False, "message": "Invalid email format"}
        if not validate_password(password):
            return {"success": False, "message": "Password must be at least 8 characters long"}

        conn = None
        cursor = None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "Database connection failed"}

            cursor = conn.cursor(dictionary=True)

            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return {"success": False, "message": "Email already registered with this user"}

            # Hash password
            hashed_pw = hash_password(password)

            # Insert user
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_pw, role)
            )
            conn.commit()

            return {"success": True, "message": f"User {role} registered successfully"}
        except Exception as e:
            return {"success": False, "message": f"⚠️ Error during registration: {e}"}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def login_user(email, password):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "Database connection failed"}

            cursor = conn.cursor(dictionary=True)

            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                return {"success": False, "message": "User not found"}

            # Verify password
            if not verify_password(password, user["password"]):
                return {"success": False, "message": "Invalid password"}

            # Distinguish role
            role = user["role"]
            if role == "admin":
                return {
                    "success": True,
                    "message": "Admin login successful",
                    "role": "admin",
                    "user": user
                }
            else:
                return {
                    "success": True,
                    "message": "Customer login successful",
                    "role": "customer",
                    "user": user
                }

        except Exception as e:
            return {"success": False, "message": f"⚠️ Error during login: {e}"}
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

