-- =========================
-- Car Rental DB (SEED DATA)
-- Run AFTER car_rental.sql
-- =========================
USE car_rental;

START TRANSACTION;

-- 1) Users (admin + customer)
-- Passwords are bcrypt-hashed for:
--   Admin:     "AdminPass123!"
--   Customer:  "CustomerPass123!"
INSERT INTO users (name, email, password, role) VALUES
('Alice Admin',    'admin@carrental.com',  '$2b$12$roomjk62e3NBDhYtZqxloeu2Ek7.l7Ea0CYvt2v6yMUdVvGCMfnwm', 'admin'),
('Carl Customer',  'carl@example.com',     '$2b$12$cW5/msidThEkBdyCqb8BA.KR3FKc9eTtMTk2tqXDII1ildSkx.pIy', 'customer');

-- 2) Cars
INSERT INTO cars
(brand, model, year, mileage, daily_rate, min_period_days, max_period_days, available_now)
VALUES
('Toyota','Corolla',       2020, 42000, 49.99, 1, 30, TRUE),
('Toyota','Camry',         2021, 36000, 59.99, 1, 30, TRUE),
('Toyota','RAV4',          2019, 58000, 69.99, 1, 30, TRUE),
('Honda','Civic',          2020, 39000, 52.00, 1, 30, TRUE),
('Honda','CR-V',           2018, 74000, 65.00, 1, 30, TRUE),
('Ford','Focus',           2019, 61000, 45.00, 1, 30, TRUE),
('Ford','Escape',          2020, 50000, 63.50, 1, 30, TRUE),
('Nissan','Sentra',        2019, 67000, 44.00, 1, 30, TRUE),
('Nissan','X-Trail',       2021, 33000, 64.00, 1, 30, TRUE),
('Hyundai','Elantra',      2022, 21000, 53.00, 1, 30, TRUE),
('Hyundai','Tucson',       2019, 59000, 60.00, 1, 30, TRUE),
('Kia','Sportage',         2020, 47000, 61.00, 1, 30, TRUE),
('Volkswagen','Golf',      2018, 82000, 42.50, 1, 30, TRUE),
('Volkswagen','Tiguan',    2021, 28500, 66.00, 1, 30, TRUE),
('BMW','3 Series',         2020, 41000, 95.00, 2, 21, TRUE),
('Mercedes-Benz','C-Class',2019, 52000, 99.00, 2, 21, TRUE),
('Audi','Q5',              2021, 30000,109.00, 2, 21, TRUE),
('Tesla','Model 3',        2022, 18000,119.00, 1, 21, TRUE),
('Tesla','Model Y',        2023, 12000,129.00, 1, 21, TRUE);

-- 3) Example booking (approved)
-- Assumes: user_id=2 (Carl), car_id=1 (Corolla), admin user_id=1
INSERT INTO bookings (user_id, car_id, start_date, end_date, status, total_cost, approved_by)
VALUES (2, 1, '2025-09-06', '2025-09-08', 'approved', 149.97, 1);

-- 4) Example payment for that booking (booking_id=1)
INSERT INTO payments (booking_id, amount, payment_method, payment_status, provider_txn_id)
VALUES (1, 149.97, 'cash', 'paid', 'DEMO-TXN-001');

-- 5) Example QR token for that booking
INSERT INTO booking_qr_codes (booking_id, qr_token, expires_at)
VALUES (1, 'QR-BOOKING-1-DEMO-TOKEN-ABC123', DATE_ADD(NOW(), INTERVAL 7 DAY));

COMMIT;
