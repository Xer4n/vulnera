from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
import hashlib
import database

h = hashlib.new('sha256')

app = Flask(__name__)
app.secret_key = "test" # needed for flash

database_file = "users.db"


database.add_product("test", "100eur", "img/papa.jpg", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum")


# Set up session configurations
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

database.initialize_db() #calls function from database.py to create the database if it does not exist, if it does then just keep using it

#Routing
@app.route("/", methods=["GET", "POST"])
def login():
    h = hashlib.new('sha256')

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        password = h.update(password.encode())
        password = h.hexdigest()

        conn = database.get_db_connection()
        cursor = conn.cursor()     

        #VULNERABLE CODE
        query = f"SELECT * FROM users WHERE username = '{username}' AND password ='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()

        
        conn.close()

        if user:
            #Using session cookies
            session["username"] = username
            session["logged_in"] = True
            session["is_admin"] = bool(user[3])
            flash(f"Login successfull for user: {user[1]}", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
                          
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    h = hashlib.new('sha256')
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        

        conn = database.get_db_connection()
        cursor = conn.cursor()

        pass_hash = h.update(password.encode())
        pass_hash = h.hexdigest()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, pass_hash))
            conn.commit()
            flash(f"User {username} registered. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already registerd!", "danger")
        finally:
            conn.close()
        
    
    return render_template("register.html")

@app.route("/home")
def home():
    if not session.get("logged_in"):
        flash("Please log in.", "danger")
        return redirect(url_for("login"))
    

    username = session.get("username", "Guest")
    is_admin = session.get("is_admin", False)


    print("DEBUG:", username, "logged in")

    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template("shop.html", username=username, products=products, is_admin=is_admin)


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
     
    if "logged_in" not in session or not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 403

    #Delete the item
    delete = database.delete_product(product_id)
    print(f"DEBUG: Deleted product: {product_id}")

    if delete:
        return jsonify({"success": True, "message": "Product deleted successfully!"}), 200
    else:
        return jsonify({"error": "Error deleting product."}), 500



@app.route("/product/<int:product_id>")
def product_page(product_id):

    product = database.get_product_by_id(product_id)

    if product:
        return render_template('product.html', product=product)
    else:
        return render_template('404.html'), 404

@app.route("/logout")
def logout():
    username = session.get("username", "Guest")

    print("DEBUG:", username, "logged out")

    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
