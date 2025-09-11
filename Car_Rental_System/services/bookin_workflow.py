# services/booking_workflow.py
from contextlib import closing
from decimal import Decimal
from ..config.database import get_connection
from ..services.payment_service import PaymentService
from ..services.qrcode_service import QRService
from ..utils.pricing import compute_total

class BookingWorkflow:
    """
    Encapsulates side-effects for booking approval:
    - set approved status/approved_by (tx)
    - ensure total_cost (compute if missing)
    - ensure pending payment (tx)
    - generate/refresh QR token (outside tx to keep flow resilient)
    """

    @staticmethod
    def approve(booking_id: int, admin_user_id: int, days_valid: int = 7):
        # 1) In-transaction work: approve + payment
        with closing(get_connection()) as conn:
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}

            with closing(conn.cursor(dictionary=True)) as cur:
                # Lock the booking row to avoid race conditions
                cur.execute(
                    """
                    SELECT booking_id, status, total_cost, user_id, car_id, start_date, end_date
                    FROM bookings
                    WHERE booking_id=%s
                    FOR UPDATE
                    """,
                    (booking_id,),
                )
                b = cur.fetchone()
                if not b:
                    return {"success": False, "message": "Booking not found"}

                if b["status"] not in ("pending", "approved", "rejected"):
                    return {"success": False, "message": f"Cannot change booking in status: {b['status']}"}

                # Set approved status + who approved
                cur.execute(
                    "UPDATE bookings SET status='approved', approved_by=%s WHERE booking_id=%s",
                    (admin_user_id, booking_id),
                )

                # Ensure total_cost exists; recompute if missing (defensive)
                total_cost = b["total_cost"]
                if total_cost is None:
                    # Fetch car constraints to compute price
                    cur.execute(
                        "SELECT daily_rate, min_period_days, max_period_days FROM cars WHERE car_id=%s",
                        (b["car_id"],),
                    )
                    car = cur.fetchone()
                    if not car:
                        return {"success": False, "message": "Related car not found"}

                    pricing = compute_total(
                        daily_rate=car["daily_rate"],
                        start=b["start_date"],  # DATE
                        end=b["end_date"],      # DATE
                        min_days=car["min_period_days"],
                        max_days=car["max_period_days"],
                        fees=[],
                        tax_rate=None,
                    )
                    total_cost = pricing["total"]
                    cur.execute(
                        "UPDATE bookings SET total_cost=%s WHERE booking_id=%s",
                        (str(total_cost), booking_id),
                    )

                # Ensure there is a pending payment (idempotent create/update)
                pay_res = PaymentService.create_or_update_pending(
                    booking_id, Decimal(str(total_cost))
                )
                if not pay_res.get("success"):
                    # Rollback on payment prepare failure
                    conn.rollback()
                    return {"success": False, "message": f"Payment prepare failed: {pay_res.get('message')}"}

                # Commit DB changes before QR generation
                conn.commit()

        # 2) Out-of-transaction work: generate/refresh QR (writes in its own call)
        qr = QRService.generate_for_booking(booking_id, days_valid=days_valid)
        # Even if QR fails, approval+payment are already consistent
        if qr.get("success"):
            return {
                "success": True,
                "message": "Booking approved; payment pending; QR generated",
                "qr_token": qr["token"],
                "qr_png": qr["png_path"],
                "expires_at": qr.get("expires_at"),
            }
        else:
            return {
                "success": True,
                "message": "Booking approved; payment pending; QR generation failed",
            }
