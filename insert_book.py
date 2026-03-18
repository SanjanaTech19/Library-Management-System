from database import get_db_connection

def add_book(title, author, isbn):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "INSERT INTO books (title, author, isbn) VALUES (%s, %s, %s)"
        cursor.execute(query, (title, author, isbn))
        conn.commit()
        print(f"✅ Success: '{title}' added to the library!")
        cursor.close()
        conn.close()

# Test the function
if __name__ == "__main__":
    add_book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565")