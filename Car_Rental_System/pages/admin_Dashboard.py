from ..controllers.admin_controller import CarController
from ..services.userservice import UserService

def admin_dashboard(current_user):
    while True:
        print(f"\n=== Admin Dashboard (Welcome {current_user['name']}) ===")
        print("1. Add Car")
        print("2. Update Car")
        print("3. Delete Car")
        print("4. List All Cars")
        print("5. Approve Booking")
        print("6. Reject Booking")
        print("7. Delete Customer")
        print("8. Scan QR for PICKUP")
        print("9. Scan QR for RETURN")
        print("10. Logout")
        ch = input("Choose: ").strip()
        if ch == "1":
            CarController.add_car(current_user)
        elif ch == "2":
            CarController.update_car(current_user)
        elif ch == "3":
            CarController.delete_car(current_user)
        elif ch == "4":
            CarController.list_all_cars(current_user)
        elif ch in ("5","6"):
            from services.booking_service import BookingService
            try:
                bid = int(input("Booking ID: "))
                approve = (ch == "5")
                res = BookingService.approve_booking(current_user["user_id"], bid, approve=approve)
                print(("✅ " if res.get("success") else "❌ ") + res.get("message"))
                if approve and res.get("qr_token"):
                    print(f"QR token: {res['qr_token']}")
                    print(f"QR PNG : {res['qr_png']}")
            except:
                print("❌ Invalid booking id")

        elif ch == "7":
            try:
                uid = int(input("Customer user_id to delete: "))
                res = UserService.delete_user(current_user["role"], uid)
                print(("✅ " if res.get("success") else "❌ ") + res.get("message"))
            except:
                print("❌ Invalid user id")
        elif ch == "8":
            from ..services.qrcode_service import QRService
            token = input("Scan/Enter QR token for PICKUP: ").strip()
            res = QRService.scan_pickup(token, current_user["user_id"])
            print(("✅ " if res.get("success") else "❌ ") + res.get("message"))

        elif ch == "9":
            from ..services.qrcode_service import QRService
            token = input("Scan/Enter QR token for RETURN: ").strip()
            res = QRService.scan_return(token, current_user["user_id"])
            print(("✅ " if res.get("success") else "❌ ") + res.get("message"))
        elif ch == "10":
            break
        else:
            print("Invalid choice")
