import sqlite3

class DatabaseConnection:
    """
    A context manager class for handling database connections automatically.
    Manages opening and closing connections, with proper error handling and cleanup.
    """
    
    def __init__(self, database_path='../users.db'):
        """
        Initialize the context manager with database path.
        
        Args:
            database_path (str): Path to the SQLite database file
        """
        self.database_path = database_path
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager - open database connection.
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        try:
            print(f"[CONNECTION] Opening database connection to {self.database_path}")
            self.connection = sqlite3.connect(self.database_path)
            self.cursor = self.connection.cursor()
            return self.connection
        except sqlite3.Error as e:
            print(f"[CONNECTION] Error opening database: {e}")
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager - handle cleanup and connection closing.
        
        Args:
            exc_type: Exception type (if any occurred)
            exc_value: Exception value (if any occurred)
            traceback: Exception traceback (if any occurred)
        
        Returns:
            bool: False to propagate exceptions, True to suppress them
        """
        if self.connection:
            try:
                if exc_type is None:
                    self.connection.commit()
                    print("[CONNECTION] Transaction committed successfully")
                else:
                    self.connection.rollback()
                    print(f"[CONNECTION] Transaction rolled back due to error: {exc_value}")
            except sqlite3.Error as e:
                print(f"[CONNECTION] Error during transaction handling: {e}")
            finally:
                self.connection.close()
                print("[CONNECTION] Database connection closed")
        
        return False

print("=== Using DatabaseConnection Context Manager ===\n")

try:
    with DatabaseConnection('users.db') as conn:
        print("=== Executing SELECT * FROM users ===")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print(f"\nQuery Results ({len(results)} rows found):")
        print("-" * 50)
        
        if results:
            for i, user in enumerate(results, 1):
                print(f"User {i}: {user}")
        else:
            print("No users found in the database")
            
except sqlite3.Error as e:
    print(f"Database error occurred: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

print("\n=== Context manager demonstration complete ===")

print("\n=== Demonstrating error handling ===")
try:
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM non_existent_table")
        results = cursor.fetchall()
        print("Results:", results)
        
except sqlite3.Error as e:
    print(f"Expected database error caught: {e}")
except Exception as e:
    print(f"Other error caught: {e}")