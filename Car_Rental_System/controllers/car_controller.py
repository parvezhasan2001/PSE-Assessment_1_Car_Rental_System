from ..utils.pricing import parse_yyyy_mm_dd
from ..utils.sessions import SessionManager
from ..services.qrcode_service import QRService
from ..utils.qrcode_utils import print_qr_ascii
from ..services.car_service import CarService
from ..services.booking_service import BookingService

class CarController:

    # ------------- internal helper -------------
    @staticmethod
    def _check_session(session_token: str, required_role: str | None = None, current_user: dict | None = None):
        """
        Returns the live session user dict or None (and prints a message) if:
          - no session / expired
          - role mismatch (when required_role is provided)
          - (optional) mismatch vs passed current_user
        """
        sess_user = SessionManager.get_user(session_token)
        if not sess_user:
            print("❌ Session expired or invalid. Please log in again.")
            return None
        if required_role and sess_user.get("role") != required_role:
            print("❌ Forbidden: requires role:", required_role)
            return None
        if current_user and sess_user.get("user_id") != current_user.get("user_id"):
            # Guard against spoofed current_user dicts passed in
            print("❌ Session/user mismatch. Please re-login.")
            return None
        return sess_user

    # ---------- ADMIN ----------
    @staticmethod
    def add_car(current_user: dict, session_token: str):
        if not CarController._check_session(session_token, required_role="admin", current_user=current_user):
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
    def update_car(current_user: dict, session_token: str):
        if not CarController._check_session(session_token, required_role="admin", current_user=current_user):
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
    def delete_car(current_user: dict, session_token: str):
        if not CarController._check_session(session_token, required_role="admin", current_user=current_user):
            return
        try:
            car_id = int(input("Car ID to delete: "))
        except Exception:
            print("❌ Invalid car id"); return
        res = CarService.delete_car(car_id)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))

    @staticmethod
    def list_all_cars(current_user: dict, session_token: str):
        if not CarController._check_session(session_token, required_role="admin", current_user=current_user):
            return
        res = CarService.list_cars()
        if not res.get("success"):
            print("❌", res.get("message")); return
        for c in res.get("cars", []):
            print(f"- #{c['car_id']}: {c['brand']} {c['model']} | rate ${c['daily_rate']} | avail={bool(c['available_now'])}")

    @staticmethod
    def customer_view_qr(current_user: dict, session_token: str):
        sess_user = CarController._check_session(session_token, required_role="customer", current_user=current_user)
        if not sess_user:
            return
        try:
            bid = int(input("Your approved booking ID: "))
        except Exception:
            print("❌ Invalid booking id"); return
        res = QRService.get_by_booking(bid)
        if not res.get("success"):
            print("❌", res.get("message")); return
        token = res["qr"]["qr_token"]
        print("\n=== Your QR (ASCII) ===")
        # If you kept the simplified utils using qrcode-terminal, you could reprint via that util.
        print_qr_ascii(token)
        print(f"\nQR token: {token} (show this at pickup)")

    # ---------- CUSTOMER ----------
    @staticmethod
    def view_available_cars():
        print("\n=== Available Cars ===")
        res = CarService.list_available_cars()
        if not res.get("success"):
            print("❌", res.get("message"))
            return
        cars = res.get("cars", [])
        if not cars:
            print("No cars available.")
            return
        for c in cars:
            print(f"- #{c['car_id']}: {c['brand']} {c['model']} | ${c['daily_rate']}/day")

    @staticmethod
    def book_car(current_user: dict, session_token: str):
        # Require a valid CUSTOMER session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="customer")
        if not sess_user:
            return

        try:
            car_id = int(input("Enter car_id to book: ").strip())
            start_s = input("Start date (YYYY-MM-DD): ").strip()
            end_s   = input("End date (YYYY-MM-DD): ").strip()
            # Basic date parsing/validation (service will re-validate too)
            start_d = parse_yyyy_mm_dd(start_s)
            end_d   = parse_yyyy_mm_dd(end_s)
            if end_d <= start_d:
                print("❌ End date must be on/after start date")
                return
        except ValueError:
            print("❌ Invalid input (numbers/dates)")
            return
        except Exception:
            print("❌ Invalid input")
            return

        res = BookingService.create_booking(sess_user["user_id"], car_id, start_s, end_s)
        if res.get("success"):
            print(f"✅ {res['message']} | Booking #{res['booking_id']} | Cost: ${res['total_cost']}")
            if "days" in res:
                print(f"   Days charged: {res['days']}")
        else:
            print("❌", res.get("message"))


    @staticmethod
    def view_my_bookings(current_user: dict, session_token: str):
        # Require a valid CUSTOMER session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="customer")
        if not sess_user:
            return

        # Optional status filter
        allowed = {"pending","approved","rejected","active","completed","cancelled"}
        flt = input("Filter by status [Enter=all | pending/approved/rejected/active/completed/cancelled]: ").strip().lower()
        status = flt if flt in allowed else None
        if flt and status is None:
            print("⚠️ Unknown status filter ignored.")

        res = BookingService.list_user_bookings(sess_user["user_id"], status=status)
        if not res.get("success"):
            print("❌", res.get("message")); return

        rows = res.get("bookings", [])
        if not rows:
            print("You have no bookings." if not status else f"No bookings with status '{flt}'.")
            return

        # Pretty print
        print("\n=== My Bookings ===")
        print(f"{'ID':<5} {'Car':<20} {'Dates':<23} {'Status':<10} {'Total':<10} {'Pay':<8} {'QR?':<4}")
        print("-" * 84)
        for r in rows:
            car = f"{r['brand']} {r['model']}"
            dates = f"{r['start_date']}→{r['end_date']}"
            total = f"${r['total_cost']}" if r['total_cost'] is not None else "-"
            pay   = r.get('payment_status') or "-"
            qr    = "Y" if r.get('qr_token') else "N"
            print(f"{r['booking_id']:<5} {car:<20} {dates:<23} {r['status']:<10} {total:<10} {pay:<8} {qr:<4}")

    # ---------- ADMIN ----------
    @staticmethod
    def add_car(current_user: dict, session_token: str):
    # Require a valid ADMIN session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="admin")
        if not sess_user:
            return

        brand = input("Brand: ").strip()
        model = input("Model: ").strip()
        if not brand or not model:
            print("❌ Brand and Model are required")
            return

        year    = input("Year (optional): ").strip()
        mileage = input("Mileage (optional): ").strip()
        rate    = input("Daily rate (e.g. 59.99): ").strip()
        min_p   = input("Min period days (optional): ").strip()
        max_p   = input("Max period days (optional): ").strip()
        avail   = input("Available now? (y/N): ").strip().lower() == "y"

        def to_int(v):  return int(v) if v else None
        def to_float(v): 
            if not v: 
                return None
            return float(v)

        try:
            year_i    = to_int(year)
            mileage_i = to_int(mileage)
            rate_f    = to_float(rate) or 0.0
            min_i     = to_int(min_p)
            max_i     = to_int(max_p)

            if rate_f < 0:
                print("❌ Daily rate must be >= 0"); return
            if mileage_i is not None and mileage_i < 0:
                print("❌ Mileage must be >= 0"); return
            if (min_i is not None and min_i <= 0) or (max_i is not None and max_i <= 0):
                print("❌ Min/Max period must be positive integers"); return
            if min_i is not None and max_i is not None and min_i > max_i:
                print("❌ Min period cannot be greater than Max period"); return

            payload = {
                "brand": brand,
                "model": model,
                "year": year_i,
                "mileage": mileage_i,
                "daily_rate": rate_f,
                "min_period_days": min_i,
                "max_period_days": max_i,
                "available_now": avail
            }
        except ValueError:
            print("❌ Invalid numeric input")
            return

        res = CarService.add_car(**payload)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))

    @staticmethod
    def update_car(current_user: dict, session_token: str):
        # Require a valid ADMIN session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="admin")
        if not sess_user:
            return

        try:
            car_id = int(input("Car ID to update: ").strip())
        except Exception:
            print("❌ Invalid car id")
            return

        print("Press Enter to skip a field")
        fields: dict = {}

        # Small helpers
        def to_int(v):
            return int(v) if v != "" else None
        def to_float(v):
            return float(v) if v != "" else None

        for key, prompt in [
            ("brand","Brand"), ("model","Model"), ("year","Year"),
            ("mileage","Mileage"), ("daily_rate","Daily rate"),
            ("min_period_days","Min days"), ("max_period_days","Max days"),
            ("available_now","Available now (y/N)")
        ]:
            raw = input(f"{prompt}: ").strip()
            if raw == "":
                continue
            try:
                if key in ("year","mileage","min_period_days","max_period_days"):
                    fields[key] = to_int(raw)
                elif key == "daily_rate":
                    fields[key] = to_float(raw)
                elif key == "available_now":
                    fields[key] = (raw.lower() == "y")
                else:
                    fields[key] = raw
            except ValueError:
                print(f"⚠️ Skipping invalid value for {key}")

        # Sanity checks if provided
        if "daily_rate" in fields and fields["daily_rate"] is not None and fields["daily_rate"] < 0:
            print("❌ Daily rate must be >= 0"); return
        if "mileage" in fields and fields["mileage"] is not None and fields["mileage"] < 0:
            print("❌ Mileage must be >= 0"); return
        if ("min_period_days" in fields and fields["min_period_days"] is not None and fields["min_period_days"] <= 0) \
           or ("max_period_days" in fields and fields["max_period_days"] is not None and fields["max_period_days"] <= 0):
            print("❌ Min/Max period must be positive integers"); return
        if fields.get("min_period_days") is not None and fields.get("max_period_days") is not None:
            if fields["min_period_days"] > fields["max_period_days"]:
                print("❌ Min period cannot be greater than Max period"); return

        res = CarService.update_car(car_id, **fields)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))


    @staticmethod
    def delete_car(current_user: dict, session_token: str):
        # Require a valid ADMIN session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="admin")
        if not sess_user:
            return

        try:
            car_id = int(input("Car ID to delete: ").strip())
        except Exception:
            print("❌ Invalid car id")
            return

        res = CarService.delete_car(car_id)
        print(("✅ " if res.get("success") else "❌ ") + res.get("message"))


    @staticmethod
    def list_all_cars(current_user: dict, session_token: str):
        # Require a valid ADMIN session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="admin")
        if not sess_user:
            return

        res = CarService.list_cars()
        if not res.get("success"):
            print("❌", res.get("message")); return
        cars = res.get("cars", [])
        if not cars:
            print("No cars found."); return
        for c in cars:
            print(f"- #{c['car_id']}: {c['brand']} {c['model']} | rate ${c['daily_rate']} | avail={bool(c['available_now'])}")


    @staticmethod
    def customer_view_qr(current_user: dict, session_token: str):
        # Require a valid CUSTOMER session
        sess_user = CarController._check_session(session_token, current_user=current_user, required_role="customer")
        if not sess_user:
            return

        try:
            bid = int(input("Your approved booking ID: ").strip())
        except Exception:
            print("❌ Invalid booking id"); return

        res = QRService.get_by_booking(bid)
        if not res.get("success") or not res.get("qr"):
            print("❌", res.get("message", "No QR token for this booking")); return

        token = res["qr"]["qr_token"]
        print("\n=== Your QR (ASCII) ===")
        # If you switched to qrcode-terminal-only utils, call that here instead.
        print_qr_ascii(token)
        print(f"\nQR token: {token} (show this at pickup)")