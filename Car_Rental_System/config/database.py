import mysql.connector
from mysql.connector import Error

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
    
