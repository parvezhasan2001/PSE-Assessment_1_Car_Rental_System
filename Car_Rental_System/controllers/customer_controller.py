# controllers/customer_controller.py
class CustomerController:
    @staticmethod
    def dashboard():
        while True:
            print("\n=== Customer Dashboard ===")
            print("1. View Available Cars")
            print("2. Book a Car")
            print("3. View My Bookings")
            print("4. Return Car")
            print("5. Logout")
            choice = input("Enter choice: ")

            if choice == "5":
                print("Logging out...")
                break
            else:
                print(f"Feature {choice} not implemented yet.")
