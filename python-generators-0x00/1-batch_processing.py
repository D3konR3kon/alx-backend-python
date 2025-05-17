
"""
Module for streaming user data from PostgreSQL database using generators
"""

import psycopg2
from psycopg2 import Error
import os


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
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def stream_users_in_batches(batch_size):
    """
    Generator function to fetch rows from user_data table in batches.
    
    Args:
        batch_size (int): Number of users to fetch in each batch
        
    Yields:
        list: A list of dictionaries containing user data for each batch
    """
    try:
        connection = connect_to_prodev()
        if not connection:
            return
          
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        batch = []
        for row in cursor:
            user = {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            batch.append(user)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
                
        if batch:
            yield batch
            
    except Exception as e:
        print(f"Error streaming user data in batches: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


def batch_processing(batch_size):
    """
    Process batches of users and filter those over age 25.
    
    Args:
        batch_size (int): Number of users to process in each batch
        
    Yields:
        list: A list of users over age 25 from each batch
    """
    
    for batch in stream_users_in_batches(batch_size):
       
        filtered_users = [user for user in batch if user['age'] > 25]
        yield filtered_users



def example_usage():
    batch_size = 6
    total_users = 0
    adult_users = 0
    
  
    for filtered_batch in batch_processing(batch_size):
        batch_count = len(filtered_batch)
        adult_users += batch_count
        
        print(f"Found {batch_count} users over age 25 in this batch:")
        for user in filtered_batch:
            print(f"  - {user['name']} (Age: {user['age']})")
        
        total_users += batch_size
    
    print(f"Processed approximately {total_users} total users")
    print(f"Found {adult_users} users over the age of 25")


if __name__ == "__main__":
    example_usage()