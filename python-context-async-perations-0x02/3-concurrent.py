import asyncio
import aiosqlite
import time

async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: All user records from the users table
    """
    print("[ASYNC_FETCH_USERS] Starting to fetch all users...")
    start_time = time.time()
    
    try:
        async with aiosqlite.connect('users.db') as db:
            async with db.execute("SELECT * FROM users") as cursor:
                results = await cursor.fetchall()
                
        end_time = time.time()
        print(f"[ASYNC_FETCH_USERS] Completed in {end_time - start_time:.3f} seconds")
        print(f"[ASYNC_FETCH_USERS] Found {len(results)} users")
        
        return results
        
    except Exception as e:
        print(f"[ASYNC_FETCH_USERS] Error: {e}")
        return []

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: User records where age > 40
    """
    print("[ASYNC_FETCH_OLDER_USERS] Starting to fetch users older than 40...")
    start_time = time.time()
    
    try:
        async with aiosqlite.connect('users.db') as db:
            async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
                results = await cursor.fetchall()
                
        end_time = time.time()
        print(f"[ASYNC_FETCH_OLDER_USERS] Completed in {end_time - start_time:.3f} seconds")
        print(f"[ASYNC_FETCH_OLDER_USERS] Found {len(results)} older users")
        
        return results
        
    except Exception as e:
        print(f"[ASYNC_FETCH_OLDER_USERS] Error: {e}")
        return []

async def fetch_concurrently():
    """
    Execute multiple database queries concurrently using asyncio.gather.
    
    Returns:
        tuple: Results from both async functions
    """
    print("=== Starting Concurrent Database Operations ===\n")
    start_time = time.time()
    
    try:
        all_users, older_users = await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users()
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n=== Concurrent Operations Completed ===")
        print(f"Total execution time: {total_time:.3f} seconds")
        print(f"All users fetched: {len(all_users)}")
        print(f"Older users fetched: {len(older_users)}")
        
        print("\n=== Sample Results ===")
        
        if all_users:
            print(f"\nFirst 3 users from all users:")
            for i, user in enumerate(all_users[:3], 1):
                print(f"  {i}. {user}")
            if len(all_users) > 3:
                print(f"  ... and {len(all_users) - 3} more")
        
        if older_users:
            print(f"\nUsers older than 40:")
            for i, user in enumerate(older_users, 1):
                print(f"  {i}. {user}")
        else:
            print("\nNo users older than 40 found")
        
        return all_users, older_users
        
    except Exception as e:
        print(f"Error in concurrent execution: {e}")
        return [], []

async def async_count_users_by_age_range(min_age, max_age):
    """
    Asynchronously count users within a specific age range.
    
    Args:
        min_age (int): Minimum age
        max_age (int): Maximum age
    
    Returns:
        int: Count of users in the age range
    """
    print(f"[COUNT_USERS] Counting users between ages {min_age} and {max_age}...")
    
    try:
        async with aiosqlite.connect('users.db') as db:
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE age BETWEEN ? AND ?", 
                (min_age, max_age)
            ) as cursor:
                result = await cursor.fetchone()
                count = result[0] if result else 0
                
        print(f"[COUNT_USERS] Found {count} users in age range {min_age}-{max_age}")
        return count
        
    except Exception as e:
        print(f"[COUNT_USERS] Error: {e}")
        return 0

async def advanced_concurrent_example():
    """
    Demonstrate running multiple different async operations concurrently.
    """
    print("\n=== Advanced Concurrent Example ===\n")
    start_time = time.time()
    
    try:
        results = await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users(),
            async_count_users_by_age_range(20, 30),
            async_count_users_by_age_range(31, 50),
            return_exceptions=True 
        )
        
        all_users, older_users, young_adults, middle_aged = results
        
        end_time = time.time()
        print(f"\nAdvanced concurrent operations completed in {end_time - start_time:.3f} seconds")
        print(f"Results summary:")
        print(f"  - Total users: {len(all_users) if isinstance(all_users, list) else 'Error'}")
        print(f"  - Users > 40: {len(older_users) if isinstance(older_users, list) else 'Error'}")
        print(f"  - Ages 20-30: {young_adults if isinstance(young_adults, int) else 'Error'}")
        print(f"  - Ages 31-50: {middle_aged if isinstance(middle_aged, int) else 'Error'}")
        
    except Exception as e:
        print(f"Error in advanced concurrent execution: {e}")

if __name__ == "__main__":
    print("Starting Asyncio Database Operations Demo\n")
    
    asyncio.run(fetch_concurrently())
    
    asyncio.run(advanced_concurrent_example())
    
    print("\n=== Demo Complete ===")

