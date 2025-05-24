import sqlite3 
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections.
    Opens a connection, passes it as the first argument to the decorated function,
    and ensures the connection is properly closed afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        conn = sqlite3.connect('users.db')
        
        try:
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    return wrapper

def transactional(func):
    """
    Decorator that manages database transactions automatically.
    Commits the transaction if the function executes successfully,
    or rolls back if an exception occurs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        
        conn = args[0] if args else None
        
        if conn is None:
            raise ValueError("No database connection found. Make sure to use @with_db_connection decorator first.")
        
        try:
            
            result = func(*args, **kwargs)
            conn.commit()
            print(f"[TRANSACTION] Successfully committed changes for {func.__name__}")
            return result
        except Exception as e:
            conn.rollback()
            print(f"[TRANSACTION] Rolled back changes for {func.__name__} due to error: {e}")
            raise e
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')