# services/car_service.py
from ..config.database import get_connection

class CarService:
    @staticmethod
    def add_car(brand, model, year=None, mileage=None,
                daily_rate=0.0, min_period_days=None, max_period_days=None,
                available_now=True):
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            sql = """
            INSERT INTO cars (brand, model, year, mileage, daily_rate, min_period_days, max_period_days, available_now)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cur.execute(sql, (brand, model, year, mileage, daily_rate, min_period_days, max_period_days, bool(available_now)))
            conn.commit()
            return {"success": True, "message": "Car added successfully", "car_id": cur.lastrowid}
        except Exception as e:
            return {"success": False, "message": f"Add car error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def update_car(car_id, **fields):
        if not fields:
            return {"success": False, "message": "No fields to update"}
        allowed = {"brand","model","year","mileage","daily_rate","min_period_days","max_period_days","available_now"}
        sets, values = [], []
        for k,v in fields.items():
            if k in allowed:
                sets.append(f"{k}=%s")
                values.append(v)
        if not sets:
            return {"success": False, "message": "No valid fields to update"}

        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)

            sql = f"UPDATE cars SET {', '.join(sets)} WHERE car_id=%s"
            values.append(car_id)
            cur.execute(sql, tuple(values))
            conn.commit()
            if cur.rowcount == 0:
                return {"success": False, "message": "Car not found"}
            return {"success": True, "message": "Car updated successfully"}
        except Exception as e:
            return {"success": False, "message": f"Update car error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def delete_car(car_id):
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)
            cur.execute("DELETE FROM cars WHERE car_id=%s", (car_id,))
            conn.commit()
            if cur.rowcount == 0:
                return {"success": False, "message": "Car not found"}
            return {"success": True, "message": "Car deleted"}
        except Exception as e:
            # If a car has bookings (FK RESTRICT), deletion will fail
            return {"success": False, "message": f"Delete car error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def get_car(car_id):
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM cars WHERE car_id=%s", (car_id,))
            car = cur.fetchone()
            if not car:
                return {"success": False, "message": "Car not found"}
            return {"success": True, "car": car}
        except Exception as e:
            return {"success": False, "message": f"Get car error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def list_cars():
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM cars ORDER BY brand, model")
            rows = cur.fetchall()
            return {"success": True, "cars": rows}
        except Exception as e:
            return {"success": False, "message": f"List cars error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()

    @staticmethod
    def list_available_cars():
        """
        Return ONLY currently available cars (no date filtering).
        """
        conn, cur = None, None
        try:
            conn = get_connection()
            if not conn or not conn.is_connected():
                return {"success": False, "message": "DB connection failed"}
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM cars WHERE available_now = TRUE")
            rows = cur.fetchall()
            return {"success": True, "cars": rows}
        except Exception as e:
            return {"success": False, "message": f"List available cars error: {e}"}
        finally:
            if cur: cur.close()
            if conn and conn.is_connected(): conn.close()
