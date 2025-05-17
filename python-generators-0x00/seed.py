#!/usr/bin/env python3
"""
Script to set up PostgreSQL database ALX_prodev with user_data table
and populate it with sample data from user_data.csv
"""

import psycopg2
import uuid
import csv
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


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist
    
    Args:
        connection: PostgreSQL database connection object
    """
    try:
        # Set autocommit to create database
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'alx_prodev'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE alx_prodev")
            print("Database 'ALX_prodev' created")
        else:
            print("Database 'ALX_prodev' already exists")
            
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


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


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields
    
    Args:
        connection: PostgreSQL database connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age INT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON user_data (user_id);
        """)
        connection.commit()
        print("Table 'user_data' created or already exists")
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, data):
    """
    Inserts data in the database if it does not exist
    
    Args:
        connection: PostgreSQL database connection object
        data: List of user data dictionaries to insert
    """
    try:
        cursor = connection.cursor()
        
        for user in data:
            cursor.execute("SELECT COUNT(*) FROM user_data WHERE user_id = %s", (user['user_id'],))
            if cursor.fetchone()[0] == 0:
                query = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                values = (user['user_id'], user['name'], user['email'], user['age'])
                cursor.execute(query, values)
                print(f"Inserted data for user: {user['name']}")
            else:
                print(f"Data for user_id {user['user_id']} already exists, skipping")
        
        connection.commit()
        print("Data insertion complete")
    except Error as e:
        print(f"Error inserting data: {e}")


def read_csv_data(file_path):
    """
    Read data from CSV file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of dictionaries containing user data
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found")
            return []
        
        data = []
        with open(file_path, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                if 'user_id' not in row or not row['user_id']:
                    row['user_id'] = str(uuid.uuid4())
                
                if 'age' in row:
                    row['age'] = int(row['age'])
                    
                data.append(row)
        
        print(f"Successfully read {len(data)} records from {file_path}")
        return data
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []


def main():
    """
    Main function to set up database and insert data
    """
    # Connect to PostgreSQL server (default database)
    connection = connect_to_postgres()
    if not connection:
        return
    
    # Create database
    create_database(connection)
    connection.close()
    
    # Connect to the ALX_prodev database
    db_connection = connect_to_prodev()
    if not db_connection:
        return
    
    # Create table
    create_table(db_connection)
    
    # Read data from CSV
    csv_file_path = "../user_data.csv"
    data = read_csv_data(csv_file_path)
    
    # Insert data into the database
    if data:
        insert_data(db_connection, data)
    
    # Close the database connection
    db_connection.close()
    print("Database operations completed")


if __name__ == "__main__":
    main()