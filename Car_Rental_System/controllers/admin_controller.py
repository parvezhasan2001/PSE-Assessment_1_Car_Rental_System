from Car_Rental_System.services.qrcode_service import QRService
from Car_Rental_System.utils.qrcode_utils import print_qr_ascii
from ..services.car_service import CarService
from ..services.booking_service import BookingService

class CarController:

    # ---------- CUSTOMER ----------
    @staticmethod
    def view_available_cars():
        print("\n=== Available Cars ===")
        start = input("Filter start date (YYYY-MM-DD) or Enter to skip: ").strip() or None
        end   = input("Filter end date (YYYY-MM-DD) or Enter to skip: ").strip() or None
        res = CarService.list_available_cars(start, end) if (start and end) else CarService.list_available_cars()
        if not res.get("success"):
            print("❌", res.get("message")); return
        cars = res.get("cars", [])
        if not cars:
            print("No cars available.")
            return
        for c in cars:
            print(f"- #{c['car_id']}: {c['brand']} {c['model']} | ${c['daily_rate']}/day")

    @staticmethod
    def book_car(current_user):
        if current_user.get("role") != "customer":
            print("❌ Only customers can book cars.")
            return
        try:
            car_id = int(input("Enter car_id to book: "))
            start  = input("Start date (YYYY-MM-DD): ").strip()
            end    = input("End date (YYYY-MM-DD): ").strip()
        except Exception:
            print("❌ Invalid input")
            return
        res = BookingService.create_booking(current_user["user_id"], car_id, start, end)
        if res.get("success"):
            print(f"✅ {res['message']} | Booking #{res['booking_id']} | Cost: ${res['total_cost']}")
        else:
            print("❌", res.get("message"))

    # ---------- ADMIN ----------
    @staticmethod
    def add_car(current_user):
        if current_user.get("role") != "admin":
            print("❌ Admin only")
            return
        brand = input("Brand: ").strip()
        model = input("Model: ").strip()
        year = input("Year (optional): ").strip() or None
        mileage = input("Mileage (optional): ").strip() or None
        rate = input("Daily rate (e.g. 59.99): ").strip() or "0"
        min_p = input("Min period days (optional): ").strip() or None
        max_p = input("Max period days (optional): ").strip() or None
        avail = input("Available now? (y/N): ").strip().lower() == "y"
        try:
            payload = {
                "brand": brand, "model": model,
                "year": int(year) if year else None,
                "mileage": int(mileage) if mileage else None,
                "daily_rate": float(rate),
                "min_period_days": int(min_p) if min_p else None,
                "max_period_days": int(max_p) if max_p else None,
                "available_now": avail
            }
        except Exception:
            print("❌ Invalid numeric input"); return
        res = CarService.add_car(**payload)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))

    @staticmethod
    def update_car(current_user):
        if current_user.get("role") != "admin":
            print("❌ Admin only")
            return
        try:
            car_id = int(input("Car ID to update: "))
        except Exception:
            print("❌ Invalid car id"); return
        print("Press Enter to skip a field")
        fields = {}
        for key, prompt in [
            ("brand","Brand"), ("model","Model"), ("year","Year"),
            ("mileage","Mileage"), ("daily_rate","Daily rate"),
            ("min_period_days","Min days"), ("max_period_days","Max days"),
            ("available_now","Available now (y/N)")
        ]:
            val = input(f"{prompt}: ").strip()
            if val == "": continue
            if key in ("year","mileage","min_period_days","max_period_days"):
                try: fields[key] = int(val)
                except: print(f"Skipping invalid {key}")
            elif key == "daily_rate":
                try: fields[key] = float(val)
                except: print("Skipping invalid rate")
            elif key == "available_now":
                fields[key] = (val.lower() == "y")
            else:
                fields[key] = val

        res = CarService.update_car(car_id, **fields)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))

    @staticmethod
    def delete_car(current_user):
        if current_user.get("role") != "admin":
            print("❌ Admin only")
            return
        try:
            car_id = int(input("Car ID to delete: "))
        except Exception:
            print("❌ Invalid car id"); return
        res = CarService.delete_car(car_id)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))

    @staticmethod
    def list_all_cars(current_user):
        if current_user.get("role") != "admin":
            print("❌ Admin only")
            return
        res = CarService.list_cars()
        if not res.get("success"):
            print("❌", res.get("message")); return
        for c in res.get("cars", []):
            print(f"- #{c['car_id']}: {c['brand']} {c['model']} | rate ${c['daily_rate']} | avail={bool(c['available_now'])}")

    @staticmethod
    def customer_view_qr():
        try:
            bid = int(input("Your approved booking ID: "))
        except:
            print("❌ Invalid booking id"); return
        res = QRService.get_by_booking(bid)
        if not res.get("success"):
            print("❌", res.get("message")); return
        token = res["qr"]["qr_token"]
        print("\n=== Your QR (ASCII) ===")
        print_qr_ascii(token)
        print(f"\nQR token: {token} (show this at pickup)")