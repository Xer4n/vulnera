import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Connect to the database and return the connection."""
    conn = psycopg2.connect(
    dbname = "vulneradb",
    user="postgres",
    password="vulnera",
    host="localhost",
    port="5432"
    )


    return conn

def initialize_db():
    """Create database tables if they do not exist and add default admin user."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            password VARCHAR(100),
            is_admin BOOLEAN NOT NULL DEFAULT FALSE,
            balance INTEGER NOT NULL DEFAULT 300
            
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price INT NOT NULL,
            image TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    #Create the comment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
                   id SERIAL PRIMARY KEY,
                   product_id INTEGER NOT NULL,
                   user_name TEXT NOT NULL,
                   comment TEXT NOT NULL,
                   timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (product_id) REFERENCES products(id)
                   )
    """)

    # Insert an admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = %s", ("admin",))
    if not cursor.fetchone():
        h = hashlib.new("sha256")
        hashed_pw = h.update("admin321".encode())
        hashed_pw = h.hexdigest()

        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
                       ("admin", hashed_pw, True))



    conn.commit()
    conn.close()


def get_user_by_id(id):
    """Get a user by their ID"""

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (int(id),))
    user = cursor.fetchone()

    return user



def get_all_users():
    '''Get all usernames, their balance and id registered in the database'''
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, balance FROM users")
    users = cursor.fetchall()

    conn.close()

    return users

def delete_user(id):
    """Delete user by id"""
    try:
        conn = get_db_connection()
        conn.autocommit = True # Allowing multiple queries.
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM users WHERE id = {id}")
        conn.commit()
        conn.close()

        return True
    except Exception as e: 
        print(f"DEBUG: Error deleting user with id: {id}", e)
        return False




def set_balance(id, balance):
    '''Set the balance of a user given the id'''
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

   
    print(f"Balance for user {id} set to {balance}")
    cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (balance, id,))
    conn.commit()
    conn.close()



def get_balance(id):
    '''Get the balance of a user given the id'''
    conn = get_db_connection()
    cursor = conn.cursor()

    #Get current balance
    cursor.execute("SELECT balance FROM users WHERE id = %s", (id,))
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
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("INSERT INTO products (name, price, image, description) VALUES (%s, %s, %s, %s)", 
                   (name, price, image, desc))
    conn.commit()
    conn.close()

def get_all_products():
    products = []
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    return products

def get_product_by_id(product_id):
    """Retrieve product by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
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
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # SQL query to delete the product by ID
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
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
    cursor = conn.cursor(cursor_factory=RealDictCursor)


    if new_password != conf_password:
        conn.close()
        return False
    else:

        pass_hash = h.update(new_password.encode())
        pass_hash = h.hexdigest()
        print(f"DEBUG: Password for user {userid} changed to {pass_hash}")
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (pass_hash, userid,))
        conn.commit()

    conn.close() 
    return True


def add_comment(product_id, name, comment):
    """Add a comment to a product"""

    conn = get_db_connection()
    cursor = conn.cursor()

    print("name", name)

    cursor.execute("INSERT INTO comments (product_id, user_name, comment) VALUES (%s, %s, %s)", (product_id, name, comment))

    conn.commit()
    conn.close()

def get_comments(product_id):
    """Get all comments for a product"""

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT user_name, comment, timestamp, id FROM comments WHERE product_id = %s ORDER BY timestamp DESC", (product_id,))

    comments = cursor.fetchall()

    conn.close()
    return comments

def delete_comment(comment_id):

    print("Deleting comment: ", comment_id)
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("DELETE from comments WHERE id = %s", (comment_id,))

    conn.commit()
    conn.close()
    

    

