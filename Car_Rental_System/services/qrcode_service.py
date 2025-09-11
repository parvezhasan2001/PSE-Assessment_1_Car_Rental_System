# services/qr_service.py
from datetime import datetime, timedelta
import secrets
from contextlib import closing
from ..config.database import get_connection   # or: from config.database import get_connection
from ..utils.qrcode_utils import print_qr_ascii as make_qr

def _new_token(n: int = 32) -> str:
    return secrets.token_urlsafe(n)[:n]   # secure, URL-safe

class QRService:
    @staticmethod
    def generate_for_booking(booking_id: int, days_valid: int = 7):
        with closing(get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute("SELECT booking_id FROM bookings WHERE booking_id=%s", (booking_id,))
                if not cur.fetchone():
                    return {"success": False, "message": "Booking not found"}

                token = _new_token()
                expires_at = datetime.now() + timedelta(days=days_valid)

                cur.execute(
                    """
                    INSERT INTO booking_qr_codes (booking_id, qr_token, expires_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE qr_token=VALUES(qr_token), expires_at=VALUES(expires_at)
                    """,
                    (booking_id, token, expires_at),
                )
                conn.commit()

                png_path = make_qr(token, filename=f"booking_{booking_id}.png", show_ascii=True)
                print(f"\nSaved PNG: {png_path}")
                print(f"QR Token:  {token}  (valid until {expires_at:%Y-%m-%d %H:%M})")
                return {"success": True, "token": token, "png_path": png_path, "expires_at": expires_at}

    @staticmethod
    def get_by_booking(booking_id: int):
        with closing(get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute("SELECT * FROM booking_qr_codes WHERE booking_id=%s", (booking_id,))
                row = cur.fetchone()
                return {"success": bool(row), "qr": row} if row else {"success": False, "message": "No QR token for this booking"}

    @staticmethod
    def scan_pickup(token: str, admin_user_id: int):
        with closing(get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute(
                    """
                    SELECT b.*, q.expires_at
                    FROM booking_qr_codes q
                    JOIN bookings b ON b.booking_id = q.booking_id
                    WHERE q.qr_token=%s
                    """,
                    (token,),
                )
                b = cur.fetchone()
                if not b:
                    return {"success": False, "message": "Invalid QR token"}
                if b["expires_at"] and datetime.now() > b["expires_at"]:
                    return {"success": False, "message": "QR token has expired"}
                if b["status"] != "approved":
                    return {"success": False, "message": f"Cannot pickup: status is '{b['status']}'"}

                cur.execute("UPDATE bookings SET status='active', approved_by=%s, pickup_at=NOW() WHERE booking_id=%s",
                            (admin_user_id, b["booking_id"]))
                cur.execute("UPDATE cars SET available_now=FALSE WHERE car_id=%s", (b["car_id"],))
                conn.commit()
                return {"success": True, "message": f"Booking {b['booking_id']} picked up (active)"}

    @staticmethod
    def scan_return(token: str, admin_user_id: int):
        with closing(get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute(
                    """
                    SELECT b.*, q.expires_at
                    FROM booking_qr_codes q
                    JOIN bookings b ON b.booking_id = q.booking_id
                    WHERE q.qr_token=%s
                    """,
                    (token,),
                )
                b = cur.fetchone()
                if not b:
                    return {"success": False, "message": "Invalid QR token"}
                if b["status"] != "active":
                    return {"success": False, "message": f"Cannot return: status is '{b['status']}'"}

                cur.execute("UPDATE bookings SET status='completed', approved_by=%s, return_at=NOW() WHERE booking_id=%s",
                            (admin_user_id, b["booking_id"]))
                cur.execute("UPDATE cars SET available_now=TRUE WHERE car_id=%s", (b["car_id"],))
                conn.commit()
                return {"success": True, "message": f"Booking {b['booking_id']} returned (completed)"}
