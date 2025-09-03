from ..services.userservice import UserService
from ..config.database import get_connection

class UserController:
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
        email = input("Enter email: ")
        password = input("Enter password: ")

        result = UserService.login_user(email, password)
        print(result["message"])
        if result["success"]:
            if result["role"] == "admin":
                print("✅ Admin logged in! Redirecting to Admin Dashboard...")
            else:
                print("✅ Customer logged in! Redirecting to Customer Dashboard...")
        else:
            print("❌", result["message"])

        return result

