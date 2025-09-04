# services/booking_service.py
from datetime import datetime

from ..services.qrcode_service import QRService
from ..config.database import get_connection

class BookingService:
    @staticmethod
    def create_booking(user_id, car_id, start_date, end_date):
        """
        Creates a booking in 'pending' status after validating date range and availability overlap.
        Calculates total_cost = days * daily_rate.
        """
        conn, cur = None, None
        try:
            # basic date validation
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            ed = datetime.strptime(end_date, "%Y-%m-%d").date()
            if ed < sd:
                return {"success": False, "message": "End date cannot be before start date"}

            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            # fetch car and rate
            cur.execute("SELECT * FROM cars WHERE car_id=%s", (car_id,))
            car = cur.fetchone()
            if not car:
                return {"success": False, "message": "Car not found"}
            if not car["available_now"]:
                # still check overlaps (maybe available_now is not maintained per-date)
                pass

            # overlap check: if any booking overlaps the requested window
            cur.execute("""
                SELECT 1
                FROM bookings
                WHERE car_id = %s
                  AND status IN ('pending','approved','active')
                  AND NOT (end_date < %s OR start_date > %s)
                LIMIT 1
            """, (car_id, sd, ed))
            if cur.fetchone():
                return {"success": False, "message": "Car is not available for those dates"}

            # cost calc
            days = (ed - sd).days + 1
            daily_rate = float(car.get("daily_rate") or 0.0)
            total_cost = round(days * daily_rate, 2)

            # create booking (pending)
            cur.execute("""
                INSERT INTO bookings (user_id, car_id, start_date, end_date, status, total_cost)
                VALUES (%s, %s, %s, %s, 'pending', %s)
            """, (user_id, car_id, sd, ed, total_cost))
            conn.commit()
            return {"success": True, "message": "Booking created (pending approval)", "booking_id": cur.lastrowid, "total_cost": total_cost}
        except Exception as e:
            return {"success": False, "message": f"Create booking error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def approve_booking(admin_user_id, booking_id, approve=True):
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT * FROM bookings WHERE booking_id=%s", (booking_id,))
            b = cur.fetchone()
            if not b:
                return {"success": False, "message": "Booking not found"}
            if b["status"] not in ("pending","approved","rejected"):
                return {"success": False, "message": f"Cannot change booking in status: {b['status']}"}

            new_status = "approved" if approve else "rejected"
            cur.execute("UPDATE bookings SET status=%s, approved_by=%s WHERE booking_id=%s",
                        (new_status, admin_user_id, booking_id))
            conn.commit()

            if new_status == "approved":
                qr_res = QRService.generate_for_booking(booking_id, days_valid=7)
                if not qr_res.get("success"):
                    return {"success": True, "message": "Booking approved, but QR generation failed"}
                return {"success": True, "message": "Booking approved; QR generated",
                        "qr_token": qr_res["token"], "qr_png": qr_res["png_path"]}
            else:
                return {"success": True, "message": "Booking rejected"}
        except Exception as e:
            return {"success": False, "message": f"Approve/Reject booking error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()
