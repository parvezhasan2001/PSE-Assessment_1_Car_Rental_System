# main.py

import os, sys
base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
# Prefer relative imports when running as a module: python -m Car_Rental_System.main

from controllers.car_controller import CarController
from controllers.user_controller import UserController
from services.userservice import UserService
from services.booking_service import BookingService
from services.payment_service import PaymentService
from services.qrcode_service import QRService
from utils.sessions import SessionManager
from config.database import DatabaseConnection




def main():
    print("=== 🚗 Car Rental System ===")

    # Create shared DB adapter and controller instances ONCE
    db = DatabaseConnection()
    car_controller = CarController(db)
    user_controller = UserController(db)

    # If you plan to call services directly from main, also instantiate them here:
    booking_service = BookingService(db)
    payment_service = PaymentService(db)
    qr_service = QRService(db)

    current_user = None
    session_token = None

    while True:
        # -------------------- MAIN MENU (not logged in) --------------------
        if not current_user:
            print("\n--- Main Menu ---")
            print("1) Register")
            print("2) Login")
            print("3) Exit")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                user_controller.register_user()

            elif choice == "2":
                result = user_controller.login_user()
                if result and result.get("success"):
                    current_user  = result["user"]
                    session_token = result.get("session_token")
                    print(f"✅ Logged in as {current_user['name']} ({current_user['role']})")
                else:
                    print("❌ Login failed:", (result or {}).get("message", "Unknown error"))

            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
            continue  # re-check loop state

        # -------------------- ADMIN MENU --------------------
        if current_user["role"] == "admin":
            print(f"\n=== Admin Menu (Welcome {current_user['name']}) ===")
            print("1) List All Cars")
            print("2) Add Car")
            print("3) Update Car")
            print("4) Delete Car")
            print("5) View ALL bookings")
            print("6) View bookings needing approval (PENDING)")
            print("7) View REJECTED bookings")
            print("8) Approve Booking")
            print("9) Reject Booking")
            print("10) View Listed Customers")
            print("11) Delete Customer")
            print("12) Scan QR for PICKUP")
            print("13) Scan QR for RETURN")
            print("14) Record Payment (mark PAID)")
            print("0) Logout")
            ch = input("Choose: ").strip()

            if ch == "1":
                car_controller.list_all_cars(current_user, session_token)
            elif ch == "2":
                car_controller.add_car(current_user, session_token)
            elif ch == "3":
                car_controller.update_car(current_user, session_token)
            elif ch == "4":
                car_controller.delete_car(current_user, session_token)

            elif ch == "5":
                res = booking_service.list_admin_bookings()
                if not res.get("success"):
                    print("❌", res.get("message")); continue
                for r in res["bookings"]:
                    print(f"#{r['booking_id']} | {r['user_name']} | {r['brand']} {r['model']} | "
                          f"{r['start_date']}→{r['end_date']} | {r['status']} | "
                          f"${r['total_cost']} | pay={r.get('payment_status') or '-'}")
                print("Counts:", res.get("counts", {}))

            elif ch == "6":
                res = booking_service.list_pending_approvals()
                if not res.get("success"):
                    print("❌", res.get("message")); continue
                for r in res["bookings"]:
                    print(f"[PENDING] #{r['booking_id']} | {r['user_name']} | {r['brand']} {r['model']} "
                          f"| {r['start_date']}→{r['end_date']} | ${r['total_cost']}")
                print("Counts:", res.get("counts", {}))

            elif ch == "7":
                res = booking_service.list_rejected()
                if not res.get("success"):
                    print("❌", res.get("message")); continue
                for r in res["bookings"]:
                    print(f"[REJECTED] #{r['booking_id']} | {r['user_name']} | {r['brand']} {r['model']} "
                          f"| {r['start_date']}→{r['end_date']} | ${r['total_cost']}")
                print("Counts:", res.get("counts", {}))

            elif ch in ("8", "9"):
                try:
                    bid = int(input("Booking ID: ").strip())
                    approve = (ch == "8")
                    res = booking_service.approve_booking(current_user["user_id"], bid, approve=approve)
                    print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
                except ValueError:
                    print("❌ Invalid booking id")

            elif ch == "10":
                user_controller.list_customers(current_user, session_token)

            elif ch == "11":
                try:
                    uid = int(input("Customer user_id to delete: ").strip())
                    # If your UserService.delete_user is instance-based, call via service instance:
                    res = UserService(db).delete_user(current_user["role"], uid)
                    print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
                except ValueError:
                    print("❌ Invalid user id")

            elif ch == "12":
                token = input("Scan/Enter QR token for PICKUP: ").strip()
                res = qr_service.scan_pickup(token, current_user["user_id"])
                print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))

            elif ch == "13":
                token = input("Scan/Enter QR token for RETURN: ").strip()
                res = qr_service.scan_return(token, current_user["user_id"])
                print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))

            elif ch == "14":
                try:
                    bid = int(input("Booking ID to mark paid: ").strip())
                    method = input("Method [cash/debit_card/credit_card/paypal]: ").strip() or "cash"
                    txn = input("Provider TXN ID (optional): ").strip() or None
                    res = payment_service.mark_paid(bid, method=method, provider_txn_id=txn)
                    print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
                except ValueError:
                    print("❌ Invalid booking id")

            elif ch == "0":
                SessionManager.invalidate(session_token)
                current_user = None
                session_token = None
                print("Logged out.")
            else:
                print("Invalid choice.")

        # -------------------- CUSTOMER MENU --------------------
        else:
            print(f"\n=== Customer Menu (Welcome {current_user['name']}) ===")
            print("1) View Available Cars")
            print("2) Book a Car")
            print("3) View My Bookings")
            print("4) Show QR for Approved Booking")
            print("0) Logout")
            ch = input("Choose: ").strip()

            if ch == "1":
                car_controller.view_available_cars()
            elif ch == "2":
                car_controller.book_car(current_user, session_token)
            elif ch == "3":
                car_controller.view_my_bookings(current_user, session_token)
            elif ch == "4":
                car_controller.customer_view_qr(current_user, session_token)
            elif ch == "0":
                SessionManager.invalidate(session_token)
                current_user = None
                session_token = None
                print("Logged out.")
            else:
                print("Invalid choice.")
        pass


if __name__ == "__main__":
    main()
