from .controllers.user_controller import UserController
from .pages.admin_Dashboard import AdminDashboard
from .pages.customer_Dashboard import CustomerDashboard

def main():
    print("=== 🚗 Car Rental System ===")
    while True:
        print("\n--- Main Menu ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            result = UserController.register_user()
            # print(result.get("message"))

        elif choice == "2":
            result = UserController.login_user()
            if result and result.get("success"):
                role = result.get("role")
                if role == "admin":
                    AdminDashboard.dashboard()
                elif role == "customer":
                    CustomerDashboard.dashboard()
                else:
                    print("❌ Unknown role. Contact system administrator.")
            else:
                print("❌ Login failed:", result.get("message"))

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    main()

