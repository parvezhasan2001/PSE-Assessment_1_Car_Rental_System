# services/booking_service.py
from contextlib import closing
from decimal import Decimal
from typing import Optional

from services.bookin_workflow import BookingWorkflow
from utils.pricing import compute_total, parse_yyyy_mm_dd
from config.database import DatabaseConnection

class BookingService:
    def __init__(self, db: DatabaseConnection|None = None):
        self.db = db or DatabaseConnection()
    
    def create_booking(self, user_id: int, car_id: int, start_date_str: str, end_date_str: str):
        try:
            start = parse_yyyy_mm_dd(start_date_str)
            end = parse_yyyy_mm_dd(end_date_str)
            if end < start:
                return {"success": False, "message": "End date must be on/after start date"}
        except Exception:
            return {"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}

        with closing(self.db.get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                # Get car pricing & constraints
                cur.execute(
                    "SELECT daily_rate, min_period_days, max_period_days FROM cars WHERE car_id=%s",
                    (car_id,),
                )
                car = cur.fetchone()
                if not car:
                    return {"success": False, "message": "Car not found"}

                # (Optional) overlap/availability checks are assumed already handled
                try:
                    pricing = compute_total(
                        daily_rate=car["daily_rate"],
                        start=start,
                        end=end,
                        min_days=car["min_period_days"],
                        max_days=car["max_period_days"],
                        fees=[],        # add fixed fees here if you want (e.g., cleaning)
                        tax_rate=None,  # set tax e.g., 0.15 if needed
                    )
                except ValueError as e:
                    return {"success": False, "message": str(e)}

                cur.execute(
                    """
                    INSERT INTO bookings (user_id, car_id, start_date, end_date, status, total_cost)
                    VALUES (%s, %s, %s, %s, 'pending', %s)
                    """,
                    (user_id, car_id, start, end, str(pricing["total"])),
                )
                conn.commit()
                booking_id = cur.lastrowid

                return {
                    "success": True,
                    "message": "Booking created (pending approval)",
                    "booking_id": booking_id,
                    "total_cost": str(pricing["total"]),
                    "days": pricing["days"],
                }


    def list_user_bookings(self, user_id: int, status: Optional[str] = None):
        """
        Return a user's bookings with car details, payment status, and QR token presence.
        Optional filter by booking status: pending/approved/rejected/active/completed/cancelled
        """
        allowed = {"pending","approved","rejected","active","completed","cancelled"}
        use_filter = status in allowed if status is not None else False

        with closing(self.db.get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                sql = """
                SELECT
                    b.booking_id, b.user_id, b.car_id,
                    b.start_date, b.end_date, b.status, b.total_cost,
                    b.approved_by, b.created_at, b.updated_at,
                    c.brand, c.model, c.daily_rate,
                    p.payment_status, p.amount AS payment_amount,
                    q.qr_token
                FROM bookings b
                JOIN cars c ON c.car_id = b.car_id
                LEFT JOIN payments p ON p.booking_id = b.booking_id
                LEFT JOIN booking_qr_codes q ON q.booking_id = b.booking_id
                WHERE b.user_id = %s
                {status_clause}
                ORDER BY b.created_at DESC
                """
                if use_filter:
                    sql = sql.format(status_clause="AND b.status = %s")
                    cur.execute(sql, (user_id, status))
                else:
                    sql = sql.format(status_clause="")
                    cur.execute(sql, (user_id,))
                rows = cur.fetchall() or []
                return {"success": True, "bookings": rows}
            


    def list_admin_bookings(self,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        date_from: Optional[str] = None,   # "YYYY-MM-DD"
        date_to: Optional[str] = None,     # "YYYY-MM-DD"
        limit: int = 200,
        offset: int = 0,
    ):
        """
        Admin: list bookings with optional filters.
        - status: one of pending/approved/rejected/active/completed/cancelled
        - user_id: filter by a specific customer
        - date_from/date_to: filter by date range on start_date (inclusive bounds)
        - pagination: limit/offset
        Returns: {success, bookings: [...], counts: {status->count}}
        """
        allowed = {"pending","approved","rejected","active","completed","cancelled"}
        where = ["1=1"]
        params = []

        if status:
            if status not in allowed:
                return {"success": False, "message": f"Invalid status '{status}'"}
            where.append("b.status = %s")
            params.append(status)

        if user_id:
            where.append("b.user_id = %s")
            params.append(user_id)

        if date_from:
            where.append("b.start_date >= %s")
            params.append(date_from)

        if date_to:
            where.append("b.start_date <= %s")
            params.append(date_to)

        where_clause = " AND ".join(where)

        with closing(self.db.get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            with closing(conn.cursor(dictionary=True)) as cur:
                # Main listing
                sql = f"""
                    SELECT
                        b.booking_id, b.user_id, b.car_id,
                        b.start_date, b.end_date, b.status, b.total_cost,
                        b.approved_by, b.created_at,
                        u.name AS user_name, u.email AS user_email,
                        c.brand, c.model, c.daily_rate,
                        p.payment_status, p.amount AS payment_amount
                    FROM bookings b
                    JOIN users u ON u.user_id = b.user_id
                    JOIN cars  c ON c.car_id = b.car_id
                    LEFT JOIN payments p ON p.booking_id = b.booking_id
                    WHERE {where_clause}
                    ORDER BY b.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(sql, (*params, int(limit), int(offset)))
                rows = cur.fetchall() or []

                # Status counts (for quick summary)
                cur.execute("""
                    SELECT status, COUNT(*) AS cnt
                    FROM bookings
                    GROUP BY status
                """)
                counts_raw = cur.fetchall() or []
                counts = {r["status"]: r["cnt"] for r in counts_raw}

                return {"success": True, "bookings": rows, "counts": counts}


    def list_pending_approvals(self, limit: int = 200, offset: int = 0):
        """Admin shortcut: bookings needing approval (status = 'pending')."""
        return self.list_admin_bookings(status="pending", limit=limit, offset=offset)

    
    def list_rejected(self, limit: int = 200, offset: int = 0):
        """Admin shortcut: rejected bookings (status = 'rejected')."""
        return self.list_admin_bookings(status="rejected", limit=limit, offset=offset)

    def approve_booking(self, admin_user_id: int, booking_id: int, approve: bool = True):
        # Reject path (simple, all inside one connection scope)
        if not approve:
            with closing(self.db.get_connection()) as conn:
                if not conn or not conn.is_connected():
                    return {"success": False, "message": "DB connection failed"}
                with closing(conn.cursor(dictionary=True)) as cur:
                    cur.execute("SELECT status FROM bookings WHERE booking_id=%s", (booking_id,))
                    row = cur.fetchone()
                    if not row:
                        return {"success": False, "message": "Booking not found"}
                    if row["status"] not in ("pending", "approved", "rejected"):
                        return {"success": False, "message": f"Cannot change booking in status: {row['status']}"}
                    cur.execute(
                        "UPDATE bookings SET status='rejected', approved_by=%s WHERE booking_id=%s",
                        (admin_user_id, booking_id),
                    )
                    conn.commit()
            return {"success": True, "message": "Booking rejected"}

        # Approve path: delegate to workflow (keeps all DB work properly scoped)
        return BookingWorkflow(self.db).approve(booking_id=booking_id, admin_user_id=admin_user_id, days_valid=7)

