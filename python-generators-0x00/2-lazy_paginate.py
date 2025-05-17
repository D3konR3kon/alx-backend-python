from seed import connect_to_prodev

def paginate_users(page_size, offset=0):
    """
    Fetch a specific page of users from the database.
    
    Args:
        page_size (int): Number of users to fetch per page
        offset (int): Number of records to skip
        
    Returns:
        list: A list of dictionaries containing user data for the requested page
    """
    try:
        connection = connect_to_prodev()
        if not connection:
            return []
            
        cursor = connection.cursor()
        query = """
            SELECT *
            FROM user_data 
            ORDER BY name 
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (page_size, offset))

        users = []
        for row in cursor:
            user = {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            users.append(user)
            
        return users
            
    except Exception as e:
        print(f"Error fetching paginated user data: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


def lazy_paginate(page_size):
    """
    Generator function that implements lazy pagination of user data.
    Only fetches the next page when needed.
    
    Args:
        page_size (int): Number of users to fetch per page
        
    Yields:
        list: A list of users for each page, one page at a time
    """
    offset = 0
    
    while True:
        current_page = paginate_users(page_size, offset)

        if not current_page:
            break
            
        yield current_page
        
        offset += page_size



def example_pagination_usage():
    page_size = 5
    total_users = 0
    
    print(f"Processing users with lazy pagination (page size: {page_size})")
    print("-" * 50)
    
    for page_number, page in enumerate(lazy_paginate(page_size), 1):
        print(f"Page {page_number} ({len(page)} users):")
        
        for user in page:
            print(f"  - {user['name']} (Email: {user['email']}, Age: {user['age']})")
        
        total_users += len(page)
        print("-" * 50)
        
        if page_number >= 3:
            print("Stopping pagination after 3 pages for demonstration")
            break
    
    print(f"Processed {total_users} users across {page_number} pages")


if __name__ == "__main__":
    example_pagination_usage()