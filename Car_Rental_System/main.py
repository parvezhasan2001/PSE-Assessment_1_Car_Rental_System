# main.py

# Robust imports: support both "python -m Car_Rental_System.main" and "python main.py"
try:
    from .controllers.car_controller import CarController
    from .controllers.user_controller import UserController
    from .services.userservice import UserService
    from .services.booking_service import BookingService
    from .services.payment_service import PaymentService
    from .services.qrcode_service import QRService
    from .utils.sessions import SessionManager         
except ImportError:
    from .controllers.car_controller import CarController
    from .controllers.user_controller import UserController
    from .services.userservice import UserService
    from .services.booking_service import BookingService
    from .services.payment_service import PaymentService
    from .services.qrcode_service import QRService
    from .utils.sessions import SessionManager
              
def main():
    print("=== 🚗 Car Rental System ===")

    # current session state
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
                result = UserController.register_user()
                # Optional: print(result.get("message"))

            elif choice == "2":
                result = UserController.login_user()
                if result and result.get("success"):
                    current_user  = result["user"]
                    session_token = result.get("session_token")  # created in your login flow
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
                CarController.list_all_cars(current_user, session_token)
            elif ch == "2":
                CarController.add_car(current_user, session_token)
            elif ch == "3":
                CarController.update_car(current_user, session_token)
            elif ch == "4":
                CarController.delete_car(current_user, session_token)
            elif ch == "5":
                res = BookingService.list_admin_bookings()
                if not res.get("success"): print("❌", res.get("message")); continue
                for r in res["bookings"]:
                    print(f"#{r['booking_id']} | {r['user_name']} | {r['brand']} {r['model']} | "
                          f"{r['start_date']}→{r['end_date']} | {r['status']} | "
                          f"${r['total_cost']} | pay={r.get('payment_status') or '-'}")
                print("Counts:", res.get("counts", {}))

            elif ch == "6":
                res = BookingService.list_pending_approvals()
                if not res.get("success"): print("❌", res.get("message")); continue
                for r in res["bookings"]:
                    print(f"[PENDING] #{r['booking_id']} | {r['user_name']} | {r['brand']} {r['model']} "
                          f"| {r['start_date']}→{r['end_date']} | ${r['total_cost']}")
                print("Counts:", res.get("counts", {}))

            elif ch == "7":
                res = BookingService.list_rejected()
                if not res.get("success"): print("❌", res.get("message")); continue
                for r in res["bookings"]:
                    print(f"[REJECTED] #{r['booking_id']} | {r['user_name']} | {r['brand']} {r['model']} "
                          f"| {r['start_date']}→{r['end_date']} | ${r['total_cost']}")
                print("Counts:", res.get("counts", {}))
            elif ch in ("8", "9"):
                try:
                    bid = int(input("Booking ID: ").strip())
                    approve = (ch == "8")
                    res = BookingService.approve_booking(current_user["user_id"], bid, approve=approve)
                    print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
                except ValueError:
                    print("❌ Invalid booking id")
            elif ch == "10":
                UserController.list_customers(current_user, session_token)
            elif ch == "11":
                try:
                    uid = int(input("Customer user_id to delete: ").strip())
                    res = UserService.delete_user(current_user["role"], uid)
                    print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
                except ValueError:
                    print("❌ Invalid user id")
            elif ch == "12":
                token = input("Scan/Enter QR token for PICKUP: ").strip()
                res = QRService.scan_pickup(token, current_user["user_id"])
                print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
            elif ch == "13":
                token = input("Scan/Enter QR token for RETURN: ").strip()
                res = QRService.scan_return(token, current_user["user_id"])
                print(("✅ " if res.get("success") else "❌ ") + res.get("message", ""))
            elif ch == "14":
                try:
                    bid = int(input("Booking ID to mark paid: ").strip())
                    method = input("Method [cash/debit_card/credit_card/paypal]: ").strip() or "cash"
                    txn = input("Provider TXN ID (optional): ").strip() or None
                    res = PaymentService.mark_paid(bid, method=method, provider_txn_id=txn)
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
                CarController.view_available_cars()
            elif ch == "2":
                CarController.book_car(current_user, session_token)
            elif ch == "3":
                CarController.view_my_bookings(current_user, session_token)
            elif ch == "4":
                CarController.customer_view_qr(current_user, session_token)
            elif ch == "0":
                SessionManager.invalidate(session_token)
                current_user = None
                session_token = None
                print("Logged out.")
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    main()