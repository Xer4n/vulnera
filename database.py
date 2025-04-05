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
            is_admin BOOLEAN NOT NULL DEFAULT 0,
            balance INTEGER NOT NULL DEFAULT 300
            
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

    #Create the comment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   product_id INTEGER NOT NULL,
                   user TEXT NOT NULL,
                   comment TEXT NOT NULL,
                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (product_id) REFERENCES products(id)
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


def set_balance(id, balance):
    conn = get_db_connection()
    cursor = conn.cursor()

   
    print(f"Balance for user {id} set to {balance}")
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (balance, id,))
    conn.commit()
    conn.close()



def get_balance(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    #Get current balance
    cursor.execute("SELECT balance FROM users WHERE id = ?", (id,))
    current_balance = cursor.fetchone()
    current_balance = current_balance[0]

    if current_balance < 0:
        current_balance = 0
        set_balance(id, current_balance)

    
    print(f"DEBUG: Balance for user {id}: {current_balance}")
    return current_balance

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
    """Delete product by the product ID"""
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

def change_password(userid, conf_password, new_password):
    """Change password of a user"""
    h = hashlib.new("sha256")
    pass_hash = ""


    conn = get_db_connection()
    cursor = conn.cursor()


    if new_password != conf_password:
        conn.close()
        return False
    else:

        pass_hash = h.update(new_password.encode())
        pass_hash = h.hexdigest()
        print(f"DEBUG: Password for user {userid} changed to {pass_hash}")
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (pass_hash, userid,))
        conn.commit()

    conn.close() 
    return True


def add_comment(product_id, user, comment):
    """Add a comment to a product"""

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO comments (product_id, user, comment) VALUES (?, ?, ?)", (product_id, user, comment))

    conn.commit()
    conn.close()

def get_comments(product_id):
    """Get all comments for a product"""

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user, comment, timestamp, id FROM comments WHERE product_id = ? ORDER BY timestamp DESC", (product_id,))

    comments = cursor.fetchall()

    conn.close()
    return comments

def delete_comment(comment_id):

    print("Deleting comment: ", comment_id)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE from comments WHERE id = ?", (comment_id,))

    conn.commit()
    conn.close()
    

    

