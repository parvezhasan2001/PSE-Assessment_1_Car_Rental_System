class Rental:
    def __init__(self, rental_id, car_id, customer_id, rental_date, return_date=None):
        self.rental_id = rental_id
        self.car_id = car_id
        self.customer_id = customer_id
        self.rental_date = rental_date
        self.return_date = return_date