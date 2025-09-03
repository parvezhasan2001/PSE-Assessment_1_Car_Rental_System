class AdminController:
    @staticmethod
    def dashboard():
        while True:
            print("\n=== Admin Dashboard ===")
            print("1. Add Car")
            print("2. Update Car")
            print("3. Delete Car")
            print("4. View All Cars")
            print("5. Approve/Reject Bookings")
            print("6. Logout")
            choice = input("Enter choice: ")

            if choice == "6":
                print("Logging out...")
                break
            else:
                print(f"Feature {choice} not implemented yet.")