from flask import Flask, render_template, request, flash, redirect

import pymysql

from dynaconf import Dynaconf

app = Flask(__name__)

config = Dynaconf( settings_file = [ "settings.toml"])

app.secret_key = config

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
 
    cursor.execute("SELECT * FROM Product WHERE ID = %s ", (product_id,) )
    
    result = cursor.fetchone()
    
    connection.close()

    return render_template("product.html.jinja", product=result)



@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        password_confrim=request.form["confirm_password"]
        address=request.form["address"]
        birthdate=request.form["birthday"]
        
        if password != password_confrim:
            flash("Passwords do not match")
        elif len(password) < 8:
         flash("Password must be at least 8 characters long")     
        else:
            connection = connect_db()
            cursor = connection = connection.cursor()

            cursor.execute(""" 
                INSERT INTO `User`(`Name`, `Password`, `Email`, `Adress`, `Birthday`, )
                VALUES(%s,%s,%s,%s,%s)
                           
            """,(name,password,email,address,birthday))
            
            return redirect('/login')
        
    return render_template("register.html.jinja")