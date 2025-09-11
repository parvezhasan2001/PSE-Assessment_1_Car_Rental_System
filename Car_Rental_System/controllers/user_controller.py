from getpass import getpass
from ..utils.sessions import SessionManager
from ..services.userservice import UserService

class UserController:
    
    @staticmethod
    def _require_admin(current_user: dict, session_token: str):
        sess = SessionManager.get_user(session_token)
        if not sess:
            print("❌ Session expired or invalid. Please log in again."); return None
        if sess.get("user_id") != current_user.get("user_id"):
            print("❌ Session/user mismatch. Please re-login."); return None
        if sess.get("role") != "admin":
            print("❌ Admin only."); return None
        return sess
    
    @staticmethod
    def register_user():
        name = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        role = input("Enter role (admin/customer): ")

        try:
            result = UserService.register_user(name, email, password, role)
            if result["success"]:
                print("✅", result["message"])
            else:
                print("❌", result["message"])
        except Exception as e:
            print("⚠️ Error during registration:", str(e))

    @staticmethod
    def login_user():
        email = input("Enter email: ").strip()
        password = getpass("Enter password: ")

        result = UserService.login_user(email, password)
        if not result or not result.get("success"):
            print("❌", (result or {}).get("message", "Login failed"))
            return result

        # Create a 1-hour session for the logged-in user
        token = SessionManager.create(result["user"], ttl_sec=3600)
        result["session_token"] = token

        role = result.get("role")
        if role == "admin":
            print("✅ Admin logged in! Redirecting to Admin Dashboard...")
        else:
            print("✅ Customer logged in! Redirecting to Customer Dashboard...")

        return result
    
    @staticmethod
    def list_customers(current_user: dict, session_token: str):
        if not UserController._require_admin(current_user, session_token): return
        q = input("Search (name/email, Enter=all): ").strip() or None
        res = UserService.list_customers(search=q)
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


