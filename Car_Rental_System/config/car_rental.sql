-- =========================
-- Car Rental DB (SCHEMA)
-- =========================
CREATE DATABASE IF NOT EXISTS car_rental
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE car_rental;

-- ========== USERS ==========
CREATE TABLE IF NOT EXISTS users (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,  -- bcrypt-safe
    role       ENUM('customer','admin') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_users_email ON users(email);

-- =========== CARS ==========
CREATE TABLE IF NOT EXISTS cars (
    car_id          INT AUTO_INCREMENT PRIMARY KEY,
    brand           VARCHAR(100) NOT NULL,
    model           VARCHAR(100) NOT NULL,
    year            INT NULL,
    mileage         INT NULL,
    daily_rate      DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    min_period_days INT NULL,
    max_period_days INT NULL,
    available_now   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_cars_available    ON cars(available_now);
CREATE INDEX idx_cars_brand_model  ON cars(brand, model);

-- ========= BOOKINGS =========
CREATE TABLE IF NOT EXISTS bookings (
    booking_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    car_id        INT NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE NOT NULL,
    status        ENUM('pending','approved','rejected','active','completed','cancelled')
                  NOT NULL DEFAULT 'pending',
    total_cost    DECIMAL(10,2) NULL,
    approved_by   INT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_bookings_user
      FOREIGN KEY (user_id) REFERENCES users(user_id)
      ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_bookings_car
      FOREIGN KEY (car_id) REFERENCES cars(car_id)
      ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_bookings_admin
      FOREIGN KEY (approved_by) REFERENCES users(user_id)
      ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT chk_booking_dates CHECK (end_date >= start_date)
) ENGINE=InnoDB;

CREATE INDEX idx_bookings_user    ON bookings(user_id);
CREATE INDEX idx_bookings_car     ON bookings(car_id);
CREATE INDEX idx_bookings_status  ON bookings(status);
CREATE INDEX idx_bookings_dates   ON bookings(start_date, end_date);

-- ========= PAYMENTS =========
CREATE TABLE IF NOT EXISTS payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    booking_id      INT NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    payment_method  ENUM('credit_card','debit_card','cash','paypal') NOT NULL DEFAULT 'cash',
    payment_status  ENUM('pending','paid','failed','refunded') NOT NULL DEFAULT 'pending',
    provider_txn_id VARCHAR(100) NULL,
    payment_date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_payments_booking
      FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_payments_booking ON payments(booking_id);
CREATE INDEX idx_payments_status  ON payments(payment_status);

-- ======= QR CODE TOKENS =======
CREATE TABLE IF NOT EXISTS booking_qr_codes (
    qr_id       INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL UNIQUE,
    qr_token    VARCHAR(128) NOT NULL UNIQUE,
    expires_at  DATETIME NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_qr_booking
      FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_qr_token ON booking_qr_codes(qr_token);

-- ============ VIEW ============
CREATE OR REPLACE VIEW v_available_cars AS
SELECT car_id, brand, model, year, mileage, daily_rate
FROM cars
WHERE available_now = TRUE;
