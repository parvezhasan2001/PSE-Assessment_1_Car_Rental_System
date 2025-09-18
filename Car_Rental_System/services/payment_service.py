# services/payment_service.py
from contextlib import closing
from decimal import Decimal
from config.database import DatabaseConnection

class PaymentService:
    def __init__(self, db: DatabaseConnection|None = None):
        self.db = db or DatabaseConnection()
    
    def create_or_update_pending(self, booking_id: int, amount: Decimal, method: str = "cash"):
        """
        Ensure a single pending payment exists for the booking with the given amount.
        If a payment exists, update it; else insert a new one.
        """
        with closing(self.db.get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute("SELECT payment_id FROM payments WHERE booking_id=%s", (booking_id,))
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "UPDATE payments SET amount=%s, payment_method=%s, payment_status='pending' WHERE payment_id=%s",
                        (str(amount), method, row["payment_id"]),
                    )
                else:
                    cur.execute(
                        "INSERT INTO payments (booking_id, amount, payment_method, payment_status) VALUES (%s, %s, %s, 'pending')",
                        (booking_id, str(amount), method),
                    )
                conn.commit()
                return {"success": True, "message": "Pending payment ready"}


    def mark_paid(self, booking_id: int, method: str = "cash", provider_txn_id: str | None = None):
        with closing(self.db.get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                cur.execute(
                    "UPDATE payments SET payment_status='paid', payment_method=%s, provider_txn_id=%s WHERE booking_id=%s",
                    (method, provider_txn_id, booking_id),
                )
                conn.commit()
                return {"success": True, "message": "Payment marked as PAID"}
