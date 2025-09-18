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
