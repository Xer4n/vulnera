from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, send_file
import sqlite3
import platform
import os
import hashlib
import database
import random
from math import floor
from flask_talisman import Talisman



h = hashlib.new('sha256')

app = Flask(__name__)
app.secret_key = "test" # needed for flash


#Vulnerble security headers
csp = {
    'default-src': ["'self'", '*', 'data:', 'unsafe-inline', 'unsafe-eval'],
    'script-src': ["'self'", '*', "'unsafe-inline'", "'unsafe-eval'"],
    'style-src': ["'self'", '*', "'unsafe-inline'"],
    'img-src': ["'self'", '*', 'data:'],
    'font-src': ["'self'", '*', 'data:'],
}

Talisman(
    app,
    content_security_policy=csp,
    frame_options="SAMEORIGIN",
    x_xss_protection=True,
    strict_transport_security=False
)

database_file = "users.db"

database.initialize_db()


# Set up session configurations
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

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
        print(user)

        
        conn.close()

        if user:
            #Using session cookies
            session["userid"] = user[0]
            session["username"] = user[1]
            session["logged_in"] = True
            session["is_admin"] = bool(user[3])

            #Weak CSRF token implementation

            session["csrf_token"] = f"static-token-{random.randint(100,199)}" #Not very random, brute forcable


            flash(f"Welcome, {user[1]}!", "success")
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
            cursor.execute("INSERT INTO users (username, password, balance) VALUES (%s, %s, %s)", (username, pass_hash, 300)) #TODO: Move to the DB file
            conn.commit()
            flash(f"User: {username}, registered. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Something went wrong, please try again!", "danger")
        finally:
            conn.close()
        
    
    return render_template("register.html")

@app.route("/home")
def home():
    if not session.get("logged_in"):
        flash("Please log in.", "danger")
        return redirect(url_for("login"))
    

    userid = session.get("userid")
    username = session.get("username", "Guest")
    is_admin = session.get("is_admin", False)


    print("DEBUG:", username, "logged in")

    products = database.get_all_products()

    return render_template("shop.html", userid=userid, username=username, products=products, is_admin=is_admin)


@app.route("/account/<int:userid>")
def account(userid):

    session_uid = session.get('userid')
    is_admin = session.get('is_admin', False)
    if int(userid) != session_uid and session.get("logged_in"):
        if is_admin:
            pass
        else:
            return redirect(url_for("home"))
        


    user = database.get_user_by_id(userid)
    

    if user:
        return render_template("account.html", user=user)
    return redirect(url_for("home"))


@app.route("/account/<int:userid>/addbalance", methods=["GET", "POST"])
def add_balance(userid):
    
    conn = database.get_db_connection()
    cursor = conn.cursor()



    if request.method == "POST":

        user_token = request.form.get("csrf_token")
        session_token = session.get("csrf_token")
       

        if user_token != session_token:
            flash(f"Invalid CSRF token detected!", "danger")
            return redirect(url_for("login"))


        code = request.form.get("code", "").strip().lower()

        print(f"Request by {userid} with code: {code} and token {user_token}")


        #TODO: Move this to a database before finishing. Also add ways for admin to add codes to the db
        active_codes = {

            "vulnera":1000,
            "sqli":200,
            "xss":400,
            "csrf":400,

        }

        if code in active_codes:
            amount = int(active_codes[code])
            cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount,userid))
            conn.commit()
            flash(f"{amount} added to your account!", "success")

        else:
            flash("Invalid code, try again.", "danger")
        

    #Fetch user
    cursor.execute("SELECT username, balance FROM users WHERE id = %s", (userid,))
    user = cursor.fetchone()
    conn.close()


    if user:
        username, balance = user
        return render_template("addbalance.html", username=username, userid=userid, balance=balance)
    else:
        flash("User not found", "danger")
        return redirect(url_for("login"))


@app.route("/delete/<int:product_id>", methods=["GET", "POST"])
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
    

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if not session.get("is_admin"):
        flash("Access denied!", "danger")
        return redirect(url_for("home"))
    
    if request.method == "POST":
        
        name = request.form.get("name")
        desc = request.form.get("desc")
        price = int(request.form.get("price"))

        #image upload, also File Inclusion vulnerability. The app doesnt check that an image is being uploaded, one can make a reverse shell here.
        image = request.files['image']

        if image:
            image_name = image.filename
            image_path = os.path.join("static/img", image_name)
            image.save(image_path)
        else:
            flash("No image uploaded")
            image = "#"

        database.add_product(name=name, price=floor(price), image=f"img/{image.filename}", desc=desc)

        flash("Product added successfully")
        return redirect(url_for("home"))
    
    return render_template("addproduct.html")

    



@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product_page(product_id):

    product = database.get_product_by_id(product_id=product_id)
    comments = database.get_comments(product_id=product_id)


    if request.method == "POST":

        user_token = request.form.get("csrf_token")


        if user_token != session.get("csrf_token"):
            session.pop('_flashes', None)
            flash(f"Invalid CSRF token!", "danger")
            return redirect(url_for("login"))



        comment = request.form.get("comment")

        if comment:
            database.add_comment(product_id,  session.get("username"), comment)
            flash("Comment added!", "success")
            return redirect(url_for("product_page", product_id=product_id))

    if product:
        return render_template('product.html', product=product, comments=comments)
    else:
        return render_template('404.html'), 404
    
@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):

    print("DELETING: ", comment_id)

    if "username" not in session:
        return jsonify({"Error":"Unauthorized"}), 403
    
    database.delete_comment(comment_id=comment_id)
    return jsonify({"success": True})


@app.route("/changepass/<int:userid>", methods=["GET", "POST"])
def change_pass(userid):

    is_admin = session.get("is_admin", False)
    if userid != session.get("userid") or not session.get("logged_in"):
        if is_admin:
            pass
        else:
            flash("Unauthorized access!", "danger")
            return redirect(url_for("logout"))
    
    if request.method == "POST":

        print(f"DEBUG: Request to change password for user with id: {userid}")

        user_token = request.form.get("csrf_token")

        print(f"token: {user_token}")

        if user_token != session.get("csrf_token"):
            session.pop('_flashes', None)
            flash(f"Invalid CSRF token!", "danger")
            return redirect(url_for("login"))


        conf_pass = request.form.get("conf_password")
        new_pass = request.form.get("new_password")

        print(f"Request details:  {user_token}, {new_pass}, {conf_pass}")
        
        valid = database.change_password(userid, conf_password=conf_pass, new_password=new_pass)


        if valid:
            flash("Password changed, please log in.", "success")

            flashes = session.get('_flashes')
            session.clear()

            if flashes:
                session['_flashes'] = flashes

            return redirect(url_for("login"))
            
    
        flash("Passwords, do not match", "danger")
        return redirect(url_for("account", userid=userid))
    

    return render_template("change_password.html", userid=userid)

    



@app.route("/logout")
def logout():
    username = session.get("username", "Guest")

    print("DEBUG:", username, "logged out")

    session.clear()
    flash("Logged out")
    return redirect(url_for("login"))


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):


    if "cart" not in session:
        session["cart"] = []


    product = database.get_product_by_id(product_id=product_id)

    
    if product:
        session["cart"].append({"id": product["id"], "name": product["name"], "price": product["price"]})
        session.modified = True
        flash(f"Added {product['name']} to the cart!", "success")

    return redirect(request.referrer)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    cart_items = session.get("cart", [])
    total_price = 0
    discount = 0
    percentage = 0



    for item in cart_items:
        
        price = float(item["price"])
        total_price += price

    if "total" not in session:
        session["total"] = total_price


    if request.method == "POST":
        total_price = session["total"]
        promo_code = request.form.get("promo_code")

        if promo_code == "10OFF":
            discount += total_price * 0.1
            percentage = 10

    final_total = total_price - discount


    session["total"] = final_total

    session.modified = True

    return render_template("cart.html", cart=cart_items, total=final_total, discount=percentage)

@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):

    if "cart" in session:
        session["cart"] = [item for item in session["cart"] if item["id"] != product_id]
        session.modified = True
        flash("Item removed from your cart!", "info")

    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    
    #Check that user is logged in.
    if "username" not in session:
        flash("Please log in", "danger")
        return redirect(url_for("login"))
    
    #user balance
    userid = session["userid"]
    print(userid)
    usr_balance = database.get_balance(userid)

    cart_items = session.get("cart", [])
    total_price = session.get("total")


    

    if request.method == "POST":

        user_token = request.form.get("csrf_token")

        if user_token != session.get("csrf_token"):
            session.pop('_flashes', None)
            flash(f"Invalid CSRF token!", "danger")
            return redirect(url_for("login"))

        if total_price > usr_balance:
            flash("User does not have enough balance to complete the purchase")
        else:
            new_balance = usr_balance - total_price
            database.set_balance(session["userid"], new_balance)
            
            session["cart"] =  []

            flash("Checkout complete! Thanks for your purchase!", "success")

    
        return redirect(url_for("home"))
    
    return render_template("checkout.html", cart=cart_items, total_price=total_price, balance=usr_balance)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("is_admin"):
        flash("Access denied")
        return redirect("/")
    
    users = database.get_all_users()

    output = ""

    if request.method == "POST":
        if "ping" in request.form:
            target = request.form.get("target")

            try:
                output = os.popen(f"ping -c 2 {target}").read()
            except:
                output = "Failed."
    

    return render_template("admin.html", users=users, output=output)
    
@app.route("/delete_user", methods=["GET","POST"])
def delete_user():

    userid = request.args.get("id")
    if not session.get("is_admin"):
        flash(f"Access denied")
        return redirect(url_for("home"))


    
    if database.delete_user(userid) and userid != 1:
        flash(f"User with id: {userid} has been deleted!", "success")
    else:
        flash(f"Error, something went wrong.", "danger")

    return redirect(url_for("admin"))



#Directory traversal vulnerability
@app.route('/view')
def view_file():
    filename = request.args.get("filename")

    if not filename:
        return "No file specified", 400
    else:
        filename = "static/" + filename
    
    image_extensions = [".png", '.jpg', ".jpeg", ".gif", ".bmp", ".webp"]

    extension = os.path.splitext(filename)

    print(filename, extension)
    if extension[1] in image_extensions:
        return send_file(filename)
    else:
        try:
            with open(filename, "r") as f:
                content = f.read()
            return f"<pre>{content}</pre>"
        except Exception as e:
            return f"Error: {e}"
        

@app.route('/init_db')
def init_db():
    
    #products
    database.add_product("One shoe", "75", "img/shoe.jpg", "One red shoe, would be even better if you had a second one!")
    database.add_product("Game boy Advanced", "120", "img/gba.jpg", "The good old classic GBA!")
    database.add_product("Smart Watch", "275", "img/watch.jpg", "Fancy time telling device")
    database.add_product("Backpack", "50", "img/bag.jpg", "A way for you to store all the items!")

    #comment
    database.add_comment(1,"admin", "I have the other")
    database.add_comment(3, "Vulnera", "Enjoy 10% off with the code: 10OFF! Apply the code at checkout!")

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)