# pages/customer_Dashboard.py
from ..controllers.admin_controller import CarController


class CustomerDashboard:
    @staticmethod
    def dashboard(current_user):
        while True:
            print(f"\n=== Customer Dashboard (Welcome {current_user['name']}) ===")
            print("1. View Available Cars")
            print("2. Book a Car")
            print("3. View My Bookings")
            print("4. Show QR for Approved Booking")
            print("5. Return Car")
            print("6. Logout")
            ch = input("Choose: ").strip()
            if ch == "1":
                CarController.view_available_cars()
            elif ch == "2":
                CarController.book_car(current_user)
            elif ch == "3":
                CarController.view_my_bookings(current_user)
            elif ch == "4":
                CarController.customer_view_qr()
            elif ch == "5":
                CarController.return_car(current_user)
            elif ch == "6":
                break
            else:
                print("Invalid choice")
