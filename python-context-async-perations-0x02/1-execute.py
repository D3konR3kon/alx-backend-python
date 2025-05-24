import sqlite3

class ExecuteQuery:
    """
    A reusable context manager that takes a query and parameters,
    manages database connection, executes the query, and returns results.
    """
    
    def __init__(self, query, params=None, database_path='users.db'):
        """
        Initialize the context manager with query and parameters.
        
        Args:
            query (str): SQL query to execute
            params (tuple/list): Parameters for the query (optional)
            database_path (str): Path to the SQLite database file
        """
        self.query = query
        self.params = params if params is not None else ()
        self.database_path = database_path
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - open connection and execute query.
        
        Returns:
            list: Results of the executed query
        """
        try:
            print(f"[EXECUTE_QUERY] Opening connection to {self.database_path}")
            
            self.connection = sqlite3.connect(self.database_path)
            self.cursor = self.connection.cursor()
            
            print(f"[EXECUTE_QUERY] Executing query: {self.query}")
            if self.params:
                print(f"[EXECUTE_QUERY] With parameters: {self.params}")
            
            if self.params:
                self.cursor.execute(self.query, self.params)
            else:
                self.cursor.execute(self.query)

            query_upper = self.query.upper().strip()
            if query_upper.startswith('SELECT'):
                self.results = self.cursor.fetchall()
                print(f"[EXECUTE_QUERY] Query returned {len(self.results)} rows")
            else:
                self.results = self.cursor.rowcount
                print(f"[EXECUTE_QUERY] Query affected {self.results} rows")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f"[EXECUTE_QUERY] Database error: {e}")
            raise
        except Exception as e:
            print(f"[EXECUTE_QUERY] Unexpected error: {e}")
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager - handle cleanup and connection closing.
        
        Args:
            exc_type: Exception type (if any occurred)
            exc_value: Exception value (if any occurred)
            traceback: Exception traceback (if any occurred)
        
        Returns:
            bool: False to propagate exceptions
        """
        if self.connection:
            try:
                if exc_type is None:
                    self.connection.commit()
                    print("[EXECUTE_QUERY] Transaction committed successfully")
                else:
                    self.connection.rollback()
                    print(f"[EXECUTE_QUERY] Transaction rolled back due to error: {exc_value}")
            except sqlite3.Error as e:
                print(f"[EXECUTE_QUERY] Error during transaction handling: {e}")
            finally:
                self.connection.close()
                print("[EXECUTE_QUERY] Database connection closed")
        
        
        return False

print("=== Using ExecuteQuery Context Manager ===\n")

try:
    query = "SELECT * FROM users WHERE age > ?"
    age_threshold = 25
    
    with ExecuteQuery(query, (age_threshold,)) as results:
        print(f"\nQuery Results for users older than {age_threshold}:")
        print("-" * 60)
        
        if results:
            for i, user in enumerate(results, 1):
                print(f"User {i}: {user}")
        else:
            print(f"No users found with age > {age_threshold}")
            
except sqlite3.Error as e:
    print(f"Database error occurred: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

print("\n" + "="*50)


print("\n=== Additional Examples ===\n")

try:
    with ExecuteQuery("SELECT COUNT(*) FROM users") as result:
        print(f"Total users in database: {result[0][0] if result else 0}")
except Exception as e:
    print(f"Error counting users: {e}")

print()

try:
    query = "SELECT * FROM users WHERE age BETWEEN ? AND ?"
    with ExecuteQuery(query, (20, 30)) as results:
        print(f"Users between ages 20-30: {len(results)} found")
        for user in results[:3]:  # Show first 3 results
            print(f"  - {user}")
        if len(results) > 3:
            print(f"  ... and {len(results) - 3} more")
except Exception as e:
    print(f"Error finding users in age range: {e}")

print()

print("=== Demonstrating Error Handling ===")
try:
    with ExecuteQuery("SELECT * FROM non_existent_table") as results:
        print("This shouldn't print")
except sqlite3.Error as e:
    print(f"Expected error caught: {e}")

print("\n=== ExecuteQuery demonstration complete ===")