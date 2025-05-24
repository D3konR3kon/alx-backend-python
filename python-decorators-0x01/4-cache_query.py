import time
import sqlite3 
import functools
import hashlib

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

query_cache = {}

def cache_query(func):
    """
    Decorator that caches the results of database queries to avoid redundant calls.
    Caches results based on the SQL query string and function arguments.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None

        if 'query' in kwargs:
            query = kwargs['query']
        elif len(args) > 1:
            for arg in args[1:]:  
                if isinstance(arg, str) and any(keyword in arg.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                    query = arg
                    break
        
        if query:
            other_args = [arg for arg in args[1:] if arg != query] 
            other_kwargs = {k: v for k, v in kwargs.items() if k != 'query'}
            
            cache_key_data = f"{func.__name__}:{query}:{str(other_args)}:{str(sorted(other_kwargs.items()))}"
            cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
            
            if cache_key in query_cache:
                print(f"[CACHE] Cache HIT for query: {query[:50]}{'...' if len(query) > 50 else ''}")
                return query_cache[cache_key]
            
            print(f"[CACHE] Cache MISS for query: {query[:50]}{'...' if len(query) > 50 else ''}")
            result = func(*args, **kwargs)
            
            query_cache[cache_key] = result
            print(f"[CACHE] Cached result for query (cache size: {len(query_cache)})")
            
            return result
        else:
            print(f"[CACHE] No query detected, executing without caching")
            return func(*args, **kwargs)
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
print("=== First call (should cache) ===")
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
print("\n=== Second call (should use cache) ===")
users_again = fetch_users_with_cache(query="SELECT * FROM users")

print(f"\nCache contains {len(query_cache)} entries")