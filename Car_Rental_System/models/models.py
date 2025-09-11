class Car:
    def __init__(self, car_id, brand, model, available=True):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.available = available

class Booking:
    def __init__(self, booking_id, user_id, car: Car, start_date, end_date, status='pending'):
        self.booking_id = booking_id
        self.user_id = user_id
        self.car = car
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

class User:
    def __init__(self, user_id, name, email, password, role="customer"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role


class Rental:
    def __init__(self, rental_id, car_id, customer_id, rental_date, return_date=None):
        self.rental_id = rental_id
        self.car_id = car_id
        self.customer_id = customer_id
        self.rental_date = rental_date
        self.return_date = return_date