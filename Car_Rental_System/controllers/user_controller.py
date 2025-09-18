from getpass import getpass

from config.database import DatabaseConnection
from services.booking_service import BookingService
from services.car_service import CarService
from services.qrcode_service import QRService
from services.userservice  import UserService
from utils.sessions import SessionManager

class UserController:

    def __init__(self, db: DatabaseConnection | None = None):
        self.db = db or DatabaseConnection()
        self.car_service = CarService(self.db)
        self.booking_service = BookingService(self.db)
        self.userservice = UserService(self.db)
        self.qr_service = QRService(self.db)
        
    def _require_admin(self, current_user: dict, session_token: str):
        sess = SessionManager.get_user(session_token)
        if not sess:
            print("❌ Session expired or invalid. Please log in again."); return None
        if sess.get("user_id") != current_user.get("user_id"):
            print("❌ Session/user mismatch. Please re-login."); return None
        if sess.get("role") != "admin":
            print("❌ Admin only."); return None
        return sess
    
    def register_user(self):
        name = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = getpass("Enter password: ")  # hide input
        role = (input("Enter role (admin/customer): ").strip().lower() or "customer")
        if role not in ("admin", "customer"):
            print("ℹ️ Invalid role provided. Defaulting to 'customer'.")
            role = "customer"
        try:
            result = self.userservice.register_user(name, email, password, role)
            if result["success"]:
                print("✅", result["message"])
            else:
                print("❌", result["message"])
        except Exception as e:
            print("⚠️ Error during registration:", str(e))

    def login_user(self):
        email = input("Enter email: ").strip()
        password = getpass("Enter password: ")

        result = self.userservice.login_user(email, password)
        if not result or not result.get("success"):
            print("❌", (result or {}).get("message", "Login failed"))
            return result

        token = SessionManager.create(result["user"], ttl_sec=3600)
        result["session_token"] = token

        role = result.get("role")
        if role == "admin":
            print("✅ Admin logged in! Redirecting to Admin Dashboard...")
        else:
            print("✅ Customer logged in! Redirecting to Customer Dashboard...")

        return result
    
    
    def list_customers(self, current_user: dict, session_token: str):
        if not self._require_admin(current_user, session_token): return
        q = input("Search (name/email, Enter=all): ").strip() or None
        res = self.userservice.list_customers(search=q)
        if not res.get("success"):
            print("❌", res.get("message")); return
        rows = res.get("customers", [])
        if not rows:
            print("No customers found."); return
        print("\n=== Customers ===")
        print(f"{'ID':<5} {'Name':<20} {'Email':<28} {'Since':<19}")
        print("-"*76)
        for r in rows:
            print(f"{r['user_id']:<5} {r['name']:<20} {r['email']:<28} {str(r['created_at'])[:19]:<19}")


