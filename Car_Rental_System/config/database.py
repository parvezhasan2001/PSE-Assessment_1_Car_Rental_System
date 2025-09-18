import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = self.get_connection()

    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "car_rental"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "root"),
                port=int(os.getenv("DB_PORT", 3306)),
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
        
