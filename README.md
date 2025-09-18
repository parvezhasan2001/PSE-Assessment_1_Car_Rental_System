# 🚗 Car Rental System

A simple yet effective **Car Rental Management System** built with **Python** and **MySQL**.  
This project demonstrates **object-oriented design** with appropriate **design patterns** and includes an **innovative feature** (QR code pickup/return) to set it apart from traditional systems.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Requirements Coverage (Checklist)](#requirements-coverage-checklist)
- [Assignment Tasks Alignment](#assignment-tasks-alignment)
- [System Architecture](#system-architecture)
- [Design Pattern Used](#design-pattern-used)
- [Innovative Feature](#innovative-feature)
- [Project Structure](#project-structure)
- [Module, Classes and Methods](#module-classes-methods)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Seed Data](#seed-data)
- [Pricing & Payment Flow](#pricing--payment-flow)
- [Validation Rules](#validation-rules)
- [System Documentation (UML)](#system-documentation-uml)
- [Testing](#-testing)
- [Windows Build (PyInstaller)](#-windows-build-pyinstaller)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Credits](#credits)

---

## 📖 Overview

This CLI application enables:
- **Customers** to browse cars, book rentals, and present **QR codes** at pickup/return.
- **Admins** to manage cars and customers, **approve/reject** bookings, **scan QR** for pickup/return, and record payments.

Key technologies:
- **MySQL** for persistence
- **bcrypt** for password hashing
- **qrcode** (PNG) & **qrcode-terminal** (ASCII QR in terminal)
- **Decimal** for accurate price calculations
- Clean layering: **controllers → models → services → utils → config**

---

## ✅ Requirements Coverage (Checklist)



| ID | Requirement                                                                                    | Status | Where/How it’s implemented                                                                                                                                                                                                                                                                                              |
| -: | ---------------------------------------------------------------------------------------------- | -----: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  a | User registration & login                                                                      |      ✅ | `controllers/user_controller.py` (CLI flows)  → `services/userservice.py` (register/login)  → password hashing/verify in `utils/auth.py` (bcrypt)                                                                                                                                                                       |
|  b | Role-based access (customer vs admin)                                                          |      ✅ | Session/role guards in `controllers/user_controller._require_admin`  and `controllers/car_controller._check_session` (enforces required role)                                                                                                                                                                           |
|  c | Car database with details (ID, make/brand, model, year, mileage, availability, min/max period) |      ✅ | Create/update/list in `services/car_service.py` (fields: brand, model, year, mileage, daily\_rate, min/max days, available\_now) ; admin CLI in `controllers/car_controller.py`                                                                                                                                         |
|  d | Admin: add/update/delete cars                                                                  |      ✅ | `controllers/car_controller.py` → `CarService.add_car/update_car/delete_car`                                                                                                                                                                                                                                            |
|  e | Customers can view available cars                                                              |      ✅ | `controllers/car_controller.view_available_cars()` → `CarService.list_available_cars()`                                                                                                                                                                                                                                 |
|  f | Booking flow: select car, dates, user details                                                  |      ✅ | `controllers/car_controller.book_car()` calls `BookingService.create_booking(...)` (parses dates, inserts pending booking)                                                                                                                                                                                              |
|  g | Rental fee calculation                                                                         |      ✅ | Core calculator in `utils/pricing.py` (`compute_total`, inclusive days, min/max rules) ; used on create in `BookingService.create_booking` and (defensively) on approve in `BookingWorkflow.approve`                                                                                                                    |
|  h | Admin booking management (approve/reject)                                                      |      ✅ | Reject path updates status to `rejected` (no QR, no payment) in `BookingService.approve_booking(..., approve=False)` ; Approve path delegates to `BookingWorkflow.approve` → ensures `total_cost`, creates/updates **pending** payment, then generates QR  with payment ops in `PaymentService` and QR in `QRService`   |

**Extras**

- Payments: PaymentService.create_or_update_pending(...) on approval; mark_paid(...) to close out payments. 


- QR codes: QRService.generate_for_booking(...) on approval; get_by_booking, scan_pickup, scan_return for lifecycle. 


- Customer “My Bookings” view: Lists bookings with car, payment status, and QR presence.

---

## 🧭 Assignment Tasks Alignment

### Task 1: Design & Architecture (LO1)
- **OO architecture** with layered modules (controllers/services/utils/models/config).
- **Design patterns** documented and selectively implemented (below).
- **High-level diagrams** included (Use Case, Class, Sequence) under **System Documentation (UML)**.

### Task 2: Innovative Solutions (LO2)
- **QR Code–based pickup and return**:
  - On approval, system generates a unique token → saves **PNG** + prints **ASCII** QR (terminal).
  - **Pickup**: scan token → booking `active`, car locked.
  - **Return**: scan token → booking `completed`, car released.
- **Industry value**: Faster counter workflow, paperless handover, foundation for mobile/IoT extension.

### Task 3: Software Evolution (LO2)
- **Maintenance plan** (summarized):
  - **Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH).
  - **Migrations**: versioned SQL in `/db/migrations` (recommend adding for future changes).
  - **Backward compatibility**: additive schema changes first; feature flags; deprecation notes.
  - **Bug fixes**: unit tests for critical flows; reproducible cases; changelog updates.
  - **Release flow**: branch per feature/bug, PR review, tag releases.
  - **Observability**: structured logging; optional audit tables (e.g., QR scans).


---

---

## ✨ Features
- **Role-based login** (admin/customer) with hashed passwords (bcrypt)
- **Admin**:
  - Add / Update / Delete cars
  - Approve / Reject bookings
  - Delete customers (safeguard: cannot delete admins)
- **Customer**:
  - View available cars (date-aware availability)
  - Create bookings (pending → admin approval)
  - View QR code for approved bookings
- **QR codes**:
  - Generated on **approval**
  - Printed as **ASCII** in terminal and saved as **PNG**
  - **Pickup**: scan token → booking → `active`, car locked
  - **Return**: scan token → booking → `completed`, car released
- **MySQL persistence** for users, cars, bookings, payments, QR tokens

---

## 🏗️ System Architecture
- The System for car_rental_system uses MVC architecture as (Model, View ,Control)

**Layers**
- **Controllers** handle input/output and route calls to services.
- **Services** encapsulate business logic and DB access.
- **Utils** centralize cross-cutting concerns (security, pricing, QR, sessions).
- **Config** offers DB connection helpers.

**Key Components**
- **UserService**: registration, login, role lookup.
- **CarService**: CRUD for cars, availability queries.
- **BookingService**: booking lifecycle (create, approve/reject).
- **PaymentService**: create/update pending payments, mark paid.
- **QRService**: generate tokens/PNGs/ASCII, scan at pickup/return.

**Interactions**
- On **create booking**: compute total via `utils/pricing.py` → store in `bookings.total_cost`.
- On **approve**: create/update **pending payment** + **generate QR** (PNG+ASCII).
- On **pickup/return**: state transitions + toggle `cars.available_now`.


---

## 🧩 Design Patterns Used

- **Factory Method (documented)** for extensible entity creation (e.g., user/vehicle subtypes). The current CLI prioritizes services; factories can be added without refactoring.
- **Singleton-like access** for DB via centralized `get_db_connection()` (scoped per call with context managers).
- **Observer** to manage the booking status change simple hook methods are provided for future extension.

---

## Libraries Used

- **Standard Library Module (not a third-party library)**

  - getpass: It hids the password field in the terminal to ensure security.

  - contexlib: It is used to manage and create context managers more easily (like: closing, suppress, ExitStack method ).

  - decimal: used for performing decimal floating-point arithmetic with more precision and control than the built-in float.

  - datetime: used for working with dates and times—like getting the current time, formatting, calculating differences, and scheduling.

  - secrets: It is used to secure tokens and passwords and it is safer than random module.

  - os: It is used to interact with the operating system.

  - re: It is used to check patterns in strings.

  - time: It provides functions to work with time values 

- **Third Party Library Module**

  - bcrypt: It is used for securely hashing and checking passwords.

  - qrcode: it is used to Generate QR codes (as images).

  - qrcode_terminal: It is used to print QR code directly in the terminal instead of saving as an image.

---

## 🚀 Innovative Feature
### QR Code–Based Pickup & Return
- On **approval**, the system creates a unique **token** per booking, stores it in `booking_qr_codes`, prints an **ASCII QR** in terminal, and saves a **PNG** in `/qrcodes`.
- Admin can **scan** (type/paste) the token in terminal:
  - **Pickup** → booking → `active`, car → `available_now = FALSE`
  - **Return** → booking → `completed`, car → `available_now = TRUE`

Why it helps:
- Faster & paperless handover
- Clear audit trail and simple terminal workflow
- Easy to extend to mobile apps / IoT locks later

---

## 🗂️ Project Structure
```text
Car_Rental_System/
│── main.py
│── config/
│ |── database.py
│ |── seed.sql
| └── car_rental.sql
│── controllers/
│ ├── user_controller.py
│ └── admin_controller.py
│── services/
│ ├── userservice.py
│ ├── car_service.py
│ ├── booking_service.py
│ └── qrcode_service.py
│── models/
│ └── models.py
│── pages/
│ ├── adminDashboard.py
│ └── customer_Dashboard.py
│── utils/
│ ├── validators.py
│ ├── auth.py # bcrypt helpers
│ └── qrcode_utils.py # PNG
│── diagrams/
│ ├── class-diagram.png
│ ├── use-case-diagram.png
│ ├── activity-diagram.png
│ └── sequence-diagram.png
│── qrcodes/
│ └── qr_codes.pngs
└── requirements.txt
```

---

## 📚Modules, Classes & Methods

- **controllers/user_controller.py** — Class UserController
- 
- _require_admin — Validate session + admin role.
- 
- register_user — Collect details and register via UserService.
- 
- login_user — Authenticate and establish a session.
- 
- list_customers — Admin-only list/search of non-admin users.
- 
- **controllers/car_controller.py** — Class CarController
- 
- _check_session — Session/role/identity guard.
- 
- add_car — Admin add car via CarService.add_car.
- 
- update_car — Admin update car fields.
- 
- delete_car — Admin delete car (handles FK constraints).
- 
- list_all_cars — Admin list of every car.
- 
- customer_view_qr — Show customer’s QR in ASCII (if any).
- 
- view_available_cars — List cars available in a date range.
- 
- book_car — Create a booking for the current user.
- 
- view_my_bookings — List the current user’s bookings.
- 
- **services/userservice.py** — Class UserService
- 
- register_user — Validate + hash (bcrypt) + insert user.
- 
- login_user — Verify credentials and return role-aware data.
- 
- list_customers — Non-admin users for admin review.
- 
- delete_user — Hard delete a customer (not admins).
- 
- services/booking_service.py — Class BookingService
- 
- create_booking — Validate, compute total, insert pending booking.
- 
- list_user_bookings — Bookings for one user.
- 
- list_admin_bookings — Admin filterable search.
- 
- list_pending_approvals — Pending bookings only.
- 
- list_rejected — Rejected bookings.
- 
- approve_booking — Reject on approve=False; delegate to workflow on approve=True.
- 
- services/bookin_workflow.py — Class BookingWorkflow
- 
- approve — Transactional approve → ensure total_cost → upsert pending payment → commit → generate QR.
- 
- **services/car_service.py** — Class CarService
- 
- add_car — Insert car with constraints/pricing.
- 
- update_car — Update car details.
- 
- delete_car — Delete car (safe error on FK).
- 
- get_car — Fetch one car by id.
- 
- list_cars — All cars (no filter).
- 
- list_available_cars — Only currently available cars.
- 
- **services/payment_service.py** — Class PaymentService
- 
- create_or_update_pending — Idempotent pending payment for a booking.
- 
- mark_paid — Mark payment as paid and record metadata.
- 
- **services/qrcode_service.py**
- 
- Module: _new_token — Generate secure URL-safe token.
- 
- Class QRService
- 
- generate_for_booking — Create/refresh booking QR with expiry.
- 
- get_by_booking — Get stored QR data for a booking.
- 
- scan_pickup — Transition approved → active (car becomes unavailable).
- 
- scan_return — Transition active → completed (car becomes available).
- 
- **utils/pricing.py**
- 
- parse_yyyy_mm_dd, rental_days, money, compute_total — Money-safe pricing utilities with min/max rules.
- 
- **utils/auth.py**
- 
- hash_password, verify_password — Bcrypt helpers for secure password storage/verification.

---

## ⚙️ Installation & Setup

### 1) Python & MySQL
- Python 3.10+ recommended
- MySQL 8.0+

### 2) Install dependencies
```bash
pip install -r requirements.txt

```
### 3) Configure DB

- Edit config/database.py to match your local MySQL credentials:

```bash

# config/database.py
import mysql.connector

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='car_rental',
            user='root',
            password='root',
            port=3306,
            autocommit=True
        )
        if connection.is_connected():
             print("✅ Database connection established!")
        else:
             print("❌ Database connection failed.")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

```

### 4) Create schema & seed data

Copy /config/schema.sql and /config/seed.sql from the sections below into files and run them in MySQL Workbench or CLI:

mysql -u root -p < config/schema.sql
mysql -u root -p < config/seed.sql

Import seed directly in MySQL workbench terminal for better results

### 5) Run the app (CLI)

- If you prefer package-style execution, add __init__.py files and run python -m Car_Rental_System.main.

## 🕹️ Usage

### Customer
- **View Available Cars** (optionally filter by dates)
- **Book Car** → status `pending`, `total_cost` computed
- **Show QR for Approved Booking** (re-print ASCII QR & PNG path)

### Admin
- **Manage Cars**: add / update / delete / list
- **Approve/Reject Bookings**
  - On approval: **pending payment** row created/updated
  - On approval: **QR** generated (PNG saved, ASCII printed)
- **Scan QR**: Pickup (→ `active`), Return (→ `completed`)
- **Record Payment**: mark **PAID** (method + optional provider txn id)

## 🧱 Database Schema

- **users**: `user_id`, `name`, `email (unique)`, `password (bcrypt)`, `role (admin|customer)`, `created_at`, `updated_at`
- **cars**: `car_id`, `brand`, `model`, `year`, `mileage`, `daily_rate`, `min_period_days`, `max_period_days`, `available_now`, `created_at`, `updated_at`
- **bookings**: `booking_id`, `user_id`, `car_id`, `start_date`, `end_date`, `status`, `total_cost`, `approved_by`, `pickup_at`, `return_at`
- **payments**: `payment_id`, `booking_id`, `amount`, `payment_method`, `payment_status`, `provider_txn_id`, `payment_date`
- **booking_qr_codes**: `qr_id`, `booking_id (UNIQUE)`, `qr_token (UNIQUE)`, `expires_at`, `created_at`

```bash

DB: car_rental
Tables: users, cars, bookings, payments, booking_qr_codes and view v_available_cars.

Place this as config/schema.sql:

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

```
### 🌱 Seed Data

```bash

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

```
---

## 💵 Pricing & Payment Flow

- **Computation** in `utils/pricing.py` using `Decimal`:
  - Inclusive day count: `(end - start) + 1`
  - Enforces `min_period_days` / `max_period_days`
  - Optional fees & tax parameters
- **On create booking**: `bookings.total_cost` is stored
- **On approval**: a **pending payment** is created or updated for that `booking_id`
- **Mark Paid**: admin action to update payment status to `paid`

---
## ✅ Validation Rules

- **Email**: format check + **unique** in DB

- **Password**: ≥ 6 characters, at least 1 uppercase & 1 number **bcrypt** hashed

- **Dates**: `end_date >= start_date`; overlap checks for availability

- **Role checks**: customer (default) and admin-only actions guarded in controllers/services

- **Session**: token verified on each dashboard action

- **Booking dates**: end_date >= start_date (also validated in service layer)

- **Avaliability**: overlap checks for pending/approved/active bookings

## 📐 System Documentation (UML)

The UML Diagrams are listed Below 

- **Class Diagram:** ![UML Class Diagram](/Car_Rental_System/diagrams/class-diagram.png)

- **Use Case:** ![Use Case Diagram](/Car_Rental_System/diagrams/use-case-diagram.png)

- **Activity Diagram:** ![Activity Diagram](/Car_Rental_System/diagrams/activity-diagram.png)

- **Sequence Diagram:** ![Sequence Diagram](/Car_Rental_System/diagrams/sequence-diagram.png)

> Diagrams are provided as images. See `/diagrams/` for the source files/screenshots you created.

---

### 🔧 Software Evolution Plan (Task 3)

- **Maintenance**
  - Structured logging (add a `utils/logging.py`); error handling with clear messages.
  - Unit tests for auth, pricing, booking state transitions.
  - Linting & CI (flake8/black + GitHub Actions).
- **Versioning**
  - Semantic Versioning: `MAJOR.MINOR.PATCH`.
  - Maintain a `CHANGELOG.md`.
- **Backward Compatibility**
  - Additive schema changes first; deprecate before remove.
  - Feature flags for risky features.
  - Migration scripts in `/db/migrations` (use timestamps in filenames).

---

## 🧪 Testing

This project uses **pytest**. The default tests focus on **utility correctness** (auth & pricing). Service/DB tests are optional and can be enabled with a dedicated **test database**.

### 1) Install dev dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov python-dotenv
```

### 2) Test layout
```
tests/
├── conftest.py                 # common fixtures (env, temp dirs)
├── test_auth.py                # bcrypt roundtrip tests
└── test_pricing.py             # rental_days & compute_total
pytest.ini                      # pytest config
.env.test.example               # template for test DB credentials (optional)
```

### 3) Running tests
```bash
# run all tests
pytest -q

# with coverage (adjust package paths if needed)
pytest --cov=controllers --cov=services --cov=utils --cov-report=term-missing
```

### 4) Optional DB integration tests
If you want to run service-level tests that require a database:

1. Create a **separate database** (e.g., `car_rental_test`) and user with limited privileges.  
2. Copy your schema/seed into that DB.  
3. Create a `.env.test` from `.env.test.example` and fill in the `TEST_DB_*` values.  
4. In your tests/fixtures, connect to the test DB and **rollback** between tests.

> Tip: keep destructive operations inside transactions and `ROLLBACK` at test teardown.

---

## 🧱 Windows Build (PyInstaller)

### CarRentalCLI – Build Instructions (Windows)
```
1) Prereqs
----------
- Python 3.10+ installed and added to PATH
- (Optional) MySQL server running; your .env must have valid DB credentials:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- .env placed in the project root next to main.py

2) Quick build
--------------
- Double-click build_windows.bat (or run from a terminal). It will:
  - create a virtual environment .venv
  - install dependencies (from requirements.txt if present)
  - run PyInstaller
  - place the exe at dist/CarRentalCLI.exe

3) Alternative: build using the spec file
-----------------------------------------
- In a terminal from the project root:
  - pip install pyinstaller
  - pyinstaller --clean CarRentalCLI.spec

4) Run the exe
--------------
- Double-click dist/CarRentalCLI.exe
- Or run from terminal: dist\CarRentalCLI.exe

5) If you read extra files at runtime
-------------------------------------
- Use a helper to resolve paths when frozen:

  # config/paths.py
  import os, sys
  def resource_path(rel_path: str) -> str:
      base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
      return os.path.join(base, rel_path)

- Then open files via resource_path('config/car_rental.sql') etc.

6) Troubleshooting
------------------
- Missing module error -> add --hidden-import=<module>
- Can't find .env or car_rental.sql -> ensure they exist and are listed in add-data
- MySQL SSL/cert issues -> pip install certifi and/or add --hidden-import=certifi
```

**build_windows.bat**
```bat
pyinstaller ^
  --onefile ^
  --clean ^
  --name CarRentalCLI ^
  --paths . ^
  --hidden-import=controllers.car_controller ^
  --hidden-import=controllers.user_controller ^
  --hidden-import=services.userservice ^
  --hidden-import=services.booking_service ^
  --hidden-import=services.payment_service ^
  --hidden-import=services.qrcode_service ^
  --hidden-import=utils.sessions ^
  --hidden-import=utils.auth ^
  --hidden-import=utils.validators ^
  --hidden-import=config.database ^
  --hidden-import=config.paths ^
  --hidden-import=mysql.connector ^
  --add-data ".env;." ^
  --add-data "config\car_rental.sql;config" ^
  main.py
```

---

## 🧰 Troubleshooting

- **ImportError (relative imports)** → use absolute imports or run as module.
- **Cursor not connected** → use one connection per method; close with context managers.
- **Login fails** → ensure bcrypt hashes are stored; `VARCHAR(255)` for password column.
- **QR issues** → ensure `./qrcodes` exists/writable; `qrcode` & `qrcode-terminal` installed.
- **Date checks** → MySQL < 8.0 ignores CHECK → enforce in Python (already implemented).

---

## 📜 License

- MIT License — see `LICENSE`.

## 👨‍💻 Credits

- Developed by **Parvez Hasan** (Software Engineer) — 2025


---

## 📦 `requirements.txt`

- Create this file in the repo root:

```bash
mysql-connector-python>=8.3.0
bcrypt>=4.1.2
qrcode>=7.4.2
qrcode-terminal>=0.8
pytest>=8.0.0
pytest-cov>=5.0.0
python-dotenv>=1.0.1

```
