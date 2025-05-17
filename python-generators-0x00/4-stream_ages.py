from seed import connect_to_prodev

def stream_user_ages():
    """
    Generator function that streams user ages one by one from the database.
    
    Yields:
        int: Age of each user, one at a time
    """
    try:
        connection = connect_to_prodev()
        if not connection:
            return
            
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        for row in cursor:
            yield row[0] 
            
    except Exception as e:
        print(f"Error streaming user ages: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


def calculate_average_age():
    """
    Calculate the average age of users without loading all data into memory.
    Uses the stream_user_ages generator to process ages one by one.
    
    Returns:
        float: The average age of all users
    """
    total_age = 0
    count = 0
    

    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count > 0:
        average_age = total_age / count
        return average_age
    else:
        return 0


def main():
    """
    Main function to calculate and display the average age of users.
    """
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    main()