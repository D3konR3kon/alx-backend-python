import psycopg2
import os
from psycopg2 import Error
from dotenv import load_dotenv

load_dotenv()

def connect_to_postgres():
    """
    Connects to the default PostgreSQL database server
    
    Returns:
        connection: PostgreSQL database connection object
    """
    try:
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",    
            password=os.getenv('DB_PASSWORD'), 
            port="5432",
            database="postgres"  # Connect to default database first       
        )
        
        print("Successfully connected to PostgreSQL server")
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL server: {e}")
        return None

def connect_to_prodev():
    """
    Connects to the ALX_prodev database in PostgreSQL
    
    Returns:
        connection: PostgreSQL database connection to ALX_prodev
    """
    try:
        connection = psycopg2.connect(
            host="localhost",
            user="postgres", 
            password=os.getenv('DB_PASSWORD'),
            port="5432",       
            database="alx_prodev"
        )
        print("Successfully connected to ALX_prodev database")
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def stream_users():
    """
    Generator function to fetch rows one by one from the user_data table.
    Uses yield to return each row individually without loading all data into memory.
    
    Yields:
        dict: A dictionary containing user data with keys: user_id, name, email, age
    """
    try:
        # Connect to the database
        connection = connect_to_prodev()
        if not connection:
            return
            
        # Create cursor and execute query
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        # Fetch and yield one row at a time
        for row in cursor:
            yield {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            
    except Exception as e:
        print(f"Error streaming user data: {e}")
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def example_usage():
    for user in stream_users():
        print(f"Processing user: {user['name']} ({user['email']})")

user_stream = stream_users()
first_user = next(user_stream)
print(f"First user: {first_user['name']}")
second_user = next(user_stream)
print(f"Second user: {second_user['name']}")