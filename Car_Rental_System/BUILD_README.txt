CarRentalCLI – Build Instructions (Windows)
=========================================

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

# Run this file to run the project

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

