import time
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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries database operations if they fail due to transient errors.
    
    Args:
        retries (int): Maximum number of retry attempts (default: 3)
        delay (int/float): Delay in seconds between retry attempts (default: 2)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        print(f"[RETRY] {func.__name__} succeeded on attempt {attempt + 1}")
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == retries:
                        print(f"[RETRY] {func.__name__} failed after {retries + 1} attempts. Final error: {e}")
                        break
                    
                    print(f"[RETRY] {func.__name__} failed on attempt {attempt + 1}: {e}")
                    print(f"[RETRY] Retrying in {delay} seconds... ({retries - attempt} attempts remaining)")
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)