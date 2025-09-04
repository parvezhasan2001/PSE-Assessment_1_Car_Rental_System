# services/qr_service.py
from datetime import datetime, timedelta
import secrets
from ..config.database import get_connection
from utils.qrcode_utils import make_qr_png, print_qr_ascii

def _new_token(n: int = 32) -> str:
    # URL-safe, opaque
    return secrets.token_urlsafe(n)[:n]

class QRService:
    @staticmethod
    def generate_for_booking(booking_id: int, days_valid: int = 7):
        """Create or refresh a QR token for a booking, persist to DB, make PNG, print ASCII."""
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            # Ensure booking exists
            cur.execute("SELECT booking_id, status, user_id FROM bookings WHERE booking_id=%s", (booking_id,))
            b = cur.fetchone()
            if not b:
                return {"success": False, "message": "Booking not found"}

            token = _new_token()
            expires_at = datetime.now() + timedelta(days=days_valid)

            # Upsert token
            sql = """
            INSERT INTO booking_qr_codes (booking_id, qr_token, expires_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE qr_token=VALUES(qr_token), expires_at=VALUES(expires_at)
            """
            cur.execute(sql, (booking_id, token, expires_at))
            conn.commit()

            png_path = make_qr_png(token, filename=f"booking_{booking_id}.png")

            # Print ASCII QR in terminal
            print("\n=== QR Code (ASCII) ===")
            print_qr_ascii(token)
            print(f"\nSaved PNG: {png_path}")
            print(f"QR Token:  {token}  (valid until {expires_at:%Y-%m-%d %H:%M})")

            return {"success": True, "token": token, "png_path": png_path, "expires_at": expires_at}
        except Exception as e:
            return {"success": False, "message": f"QR generate error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def get_by_booking(booking_id: int):
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM booking_qr_codes WHERE booking_id=%s", (booking_id,))
            row = cur.fetchone()
            if not row:
                return {"success": False, "message": "No QR token for this booking"}
            return {"success": True, "qr": row}
        except Exception as e:
            return {"success": False, "message": f"QR fetch error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def scan_pickup(token: str, admin_user_id: int):
        """Simulate scanning at pickup: requires approved status -> set to active, lock car."""
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            # Resolve booking by token
            cur.execute("""
                SELECT b.*
                FROM booking_qr_codes q
                JOIN bookings b ON b.booking_id = q.booking_id
                WHERE q.qr_token=%s
            """, (token,))
            b = cur.fetchone()
            if not b:
                return {"success": False, "message": "Invalid QR token"}
            # Expiry check
            cur.execute("SELECT expires_at FROM booking_qr_codes WHERE qr_token=%s", (token,))
            row = cur.fetchone()
            if row and row["expires_at"] and datetime.now() > row["expires_at"]:
                return {"success": False, "message": "QR token has expired"}

            if b["status"] != "approved":
                return {"success": False, "message": f"Cannot pickup: booking status is '{b['status']}'"}

            # Activate booking and lock car availability
            cur.execute("UPDATE bookings SET status='active', approved_by=%s WHERE booking_id=%s",
                        (admin_user_id, b["booking_id"]))
            cur.execute("UPDATE cars SET available_now=FALSE WHERE car_id=%s", (b["car_id"],))
            conn.commit()
            return {"success": True, "message": f"Booking {b['booking_id']} picked up (active)"}
        except Exception as e:
            return {"success": False, "message": f"Pickup scan error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def scan_return(token: str, admin_user_id: int):
        """Simulate scanning at return: requires active status -> set to completed, free car."""
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            cur.execute("""
                SELECT b.*
                FROM booking_qr_codes q
                JOIN bookings b ON b.booking_id = q.booking_id
                WHERE q.qr_token=%s
            """, (token,))
            b = cur.fetchone()
            if not b:
                return {"success": False, "message": "Invalid QR token"}

            if b["status"] != "active":
                return {"success": False, "message": f"Cannot return: booking status is '{b['status']}'"}

            cur.execute("UPDATE bookings SET status='completed', approved_by=%s WHERE booking_id=%s",
                        (admin_user_id, b["booking_id"]))
            cur.execute("UPDATE cars SET available_now=TRUE WHERE car_id=%s", (b["car_id"],))
            conn.commit()
            return {"success": True, "message": f"Booking {b['booking_id']} returned (completed)"}
        except Exception as e:
            return {"success": False, "message": f"Return scan error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()
