from flask import Flask, render_template

import pymysql

from dynaconf import Dynaconf

app = Flask(__name__)

config = Dynaconf( settings_file = [ "settings.toml"])

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
    return render_template("browse.html.jinja")
