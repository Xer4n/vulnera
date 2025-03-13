import sqlite3
import hashlib

DB_NAME = "users.db"

def get_db_connection():
    """Connect to the database and return the connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like row access
    return conn

def initialize_db():
    """Create database tables if they do not exist and add default admin user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT NOT NULL,
            desc TEXT NOT NULL
        )
    """)

    # Insert an admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        h = hashlib.new("sha256")
        hashed_pw = h.update("admin321".encode())
        hashed_pw = h.hexdigest()

        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                       ("admin", hashed_pw, True))

    conn.commit()
    conn.close()


def add_product(name, price, image, desc):
    """Add a new product to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, image, desc) VALUES (?, ?, ?, ?)", 
                   (name, price, image, desc))
    conn.commit()
    conn.close()

def get_product_by_id(product_id):
    """Retrieve product by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if product:
            #Return the product in the form of a dictionary
            return {
                "id":product[0],
                "name":product[1],
                "price":product[2],
                "image":product[3],
                "desc":product[4]

            }
        else:
            return None
    except Exception as e:
        print(f"DEBUG: Error fetching product {e}")
        return None
    finally:
        conn.close()

def delete_product(product_id):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # SQL query to delete the product by ID
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        # Check if a row was affected
        if cursor.rowcount == 0:
            return False  # No product found with the given ID, deletion didn't happen

        return True  # Deletion successful
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False
    finally:
        conn.close()
