from flask import Flask, render_template, request, flash, redirect, abort

from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import pymysql

from dynaconf import Dynaconf

app = Flask(__name__)

config = Dynaconf( settings_file = [ "settings.toml"])

app.secret_key = config.secret_key

login_manager = LoginManager( app )
login_manager.login_view = '/login'

class User:
    is_authenticated = True
    is_active = True
    is_anonymous = False

    def __init__(self, result):
        self.name = result['Name']
        self.email = result['Email']
        self.address = result['Address']
        self.id = result['ID']

    def get_id(self):
        return str(self.id)
    
@login_manager.user_loader
def load_user(user_id):
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM User WHERE ID = %s", (user_id) )

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None
    
    return User(result)



def connect_db():
    conn = pymysql.connect(
        host="db.steamcenter.tech",
        user="ANunez2",
        password=config.password,
        database="ANunez2_fancy_jewels",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn



@app.route("/")
def index():
    return render_template("homepage.html.jinja")




@app.route("/Browse")
def browes():
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` ")

    result = cursor.fetchall()

    connection.close()

    return render_template("browse.html.jinja", products=result)
    return render_template("browse.html.jinja")





@app.route("/product/<product_id>")
def product_page(product_id):
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` WHERE `ID` = %s", (product_id,) )

    result = cursor.fetchone()

    connection .close() 

    if result is None:
        abort(404)

    return render_template("product.html.jinja", product=result)

@app.route("/product/<product_id>/add_to_cart", methods=["POST"])
@login_required
def add_to_cart(product_id):
    connection = connect_db()
    cursor = connection.cursor()

    quantity = request.form.get("quantity", 1) 
    user_id = current_user.id  

    cursor.execute(
        """
        INSERT INTO Cart (Quantity, ProductID, UserID)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        Quantity = Quantity + %s 
        """,
        (quantity, product_id, user_id, quantity)
    )

    connection.commit() 
    connection.close()

    return redirect("/cart")



@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        password_confrim=request.form["confirm_password"]
        address=request.form["address"]
        birthday=request.form["birthday"]
        
        if password != password_confrim:
            flash("Passwords do not match")
        elif len(password) < 8:
         flash("Password must be at least 8 characters long")     
        else:
            connection = connect_db()
            cursor = connection = connection.cursor()

            cursor.execute(""" 
                INSERT INTO `User`(`Name`, `Password`, `Email`, `Address`, `Birthday` )
                VALUES(%s,%s,%s,%s,%s)
                           
            """,(name,password,email,address,birthday))
            
            return redirect('/login')
        
    return render_template("register.html.jinja")

@app.route("/logout", methods= ["POST", "GET"])
def logout():
    logout_user()
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get('email')
        password = request.form.get('password')

        connection = connect_db()

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM User WHERE Email = %s", (email,))

        print(cursor)

        result = cursor.fetchone()

        connection.close()

        if result is None:
            flash("Email not registered!")
        elif password != result['Password']:
            flash("Incorrect password!")
        else:
            login_user(User(result))
            return redirect('/browse')
       
        
    return render_template("login.html.jinja")



@app.route('/cart')
@login_required
def cart():
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM `Cart`
        JOIN `Product` ON `Product`.`ID` = `Cart`.`ProductID`
        WHERE `UserID` = %s
    """, (current_user.id) )

    results = cursor.fetchall()

    connection.close()

    return render_template("cart.html.jinja", cart=results)


@app.route("/cart/<product_id>/update_qty", methods=["POST"])
@login_required
def update_cart(product_id):
    new_qty = request.form["qty"]

    connection= connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE `Cart`
        SET `Quantity` = %s
        WHERE `ProductID` = %s AND `UserID` = %s
    """, (new_qty, product_id, current_user.id) )

    connection.close()

    return redirect('/cart')

@app.route("/cart/<product_id>/remove", methods=["POST"])
@login_required
def remove(product_id):
    
    connection= connect_db()
    cursor = connection.cursor()

    cursor.execute("""

        DELETE FROM `Cart`
        WHERE `ProductID` = %s AND `UserID` = %s""", (product_id, current_user.id )) 

    connection.close()

    return redirect('/cart')


@app.route('/checkout')
@login_required
def checkout():
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM `Cart`
        JOIN `Product` ON `Product`.`ID` = `Cart`.`ProductID`
        WHERE `UserID` = %s
    """, (current_user.id) )

    results = cursor.fetchall()

    if request.method == "POST":
        #create the order in the database
        cursor.execute("INSERT INTO `CartTwo` (`UserID`,) VALUES (%s, %s)", (current_user.id, ) )
        
        #store products bought
        
        sale = cursor.lastrowid 
        for item in results:
            cursor.execute("""
                INSERT INTO `SaleProduct`
                            (`CartID`, `ProductID,` Quantity`)
                VALUES 
                           (%s, %s, %s)
            """, (sale, items ['ProductID'], item['Quantity']) )
        #empty cart
        cursor.execute("DELETE FROM `Cart` WHERE `UserID` = %s", (current_user.id,) )
        #goodbye message
        #TODO: Make thank you page + route
        return redirect ("/thank_you")


    connection.close()

    return render_template("checkout.html.jinja", cart=results)

@app.route("/checkout/<product_id>/update_qty", methods=["POST"])
@login_required
def checkout_update(product_id):
    new_qty = request.form["qty"]

    connection= connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE `Cart`
        SET `Quantity` = %s
        WHERE `ProductID` = %s AND `UserID` = %s
    """, (new_qty, product_id, current_user.id) )

    connection.close()

    return redirect('/checkout')

@app.route("/checkout/<product_id>/remove", methods=["POST"])
@login_required
def remove_from_checkout(product_id):
    
    connection= connect_db()
    cursor = connection.cursor()

    cursor.execute("""

        DELETE FROM `Cart`
        WHERE `ProductID` = %s AND `UserID` = %s""", (product_id, current_user.id )) 

    connection.close()

    return redirect('/checkout')