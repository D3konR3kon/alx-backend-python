import sqlite3
import functools
from datetime import datetime


def log_queries(func):
    """
    Decorator that logs SQL queries executed by database functions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'query' in kwargs:
            query = kwargs['query']
        elif args and isinstance(args[0], str):
            query = args[0]
        else:
            query = None
            for arg in args:
                if isinstance(arg, str) and any(keyword in arg.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                    query = arg
                    break
        
    
        if query:
            print(f"[{datetime.time()}] [SQL QUERY LOG] Executing: {query}")
        else:
            print(f"[{datetime.time()}] [SQL QUERY LOG] Executing function: {func.__name__}")
        
        result = func(*args, **kwargs)
        
        return result
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

users = fetch_all_users(query="SELECT * FROM users")