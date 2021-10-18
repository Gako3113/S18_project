# -*- coding: utf-8 -*-
from flask import Flask,render_template, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from tempfile import mkdtemp
import mysql.connector
from datetime import datetime
import os

conn = mysql.connector.connect(
    host= 'localhost',
    user= 'root',
    password='*****'
)

cur=conn.cursor()

cur.execute("USE travel")
conn.commit()


app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)




@app.route("/")
def layout():
    return render_template("login.html", url="url")

@app.route("/top")
def top():
    cur.execute("SELECT * FROM trip WHERE trip_id IN (SELECT trip_id FROM trip_join WHERE user_id = %s)",(session["user_id"],))
    trip_results = cur.fetchall()
    return render_template("top.html", results=trip_results)

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        user_id = request.form.get("email")
        user_name = request.form.get("user_name")
        password = generate_password_hash(request.form.get("password"))

        cur.execute("INSERT INTO user (user_id, user_name, password) VALUES (%s,%s,%s);", (user_id, user_name, password))
        conn.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        #try:
            user_id = request.form.get("user_id")
            cur.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
            user_results = cur.fetchall()

            if check_password_hash(user_results[0][2], request.form.get("password")):
                session["user_id"] = user_id
                return redirect("/top")
            else:
                return render_template("login.html")
        #except:
            #return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return render_template("login.html")


@app.route("/travel_register",methods=["POST","GET"])
def travel_register():
    if request.method == "POST":
        trip_name = request.form.get("trip_name")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        #開始日を取得
        start = datetime.strptime(start_date, '%Y-%m-%d')
        #終了日を取得
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        cur.execute("INSERT INTO trip (trip_name, start_date, end_date) VALUES (%s,%s,%s);", (trip_name, start_date, end_date))
        conn.commit()

        cur.execute("SELECT * FROM user WHERE user_id = %s;",(session["user_id"],))
        user_results = cur.fetchall()

        cur.execute("SELECT * FROM trip WHERE trip_name = %s;",(trip_name,))
        trip_results = cur.fetchall()

        #session["trip_id"] = trip_results[0][0]

        cur.execute("INSERT INTO trip_join (trip_id, user_id) VALUES (%s,%s);", (trip_results[0][0], session["user_id"]))
        conn.commit()

        return render_template("travel.html",user_name=user_results[0][1],start_date=start_date,end_date=end_date)
    else:
        return render_template("travel_register.html")

@app.route("/travel",methods=["POST"])
def travel():
    trip_name = request.form.get("trip_name")
    cur.execute("SELECT * FROM user WHERE user_id = %s;",(session["user_id"],))
    user_results = cur.fetchall()

    cur.execute("SELECT * FROM trip WHERE trip_name = %s;",(trip_name,))
    trip_results = cur.fetchall()
    return render_template("travel.html",user_name=user_results[0][1], trip_name=trip_name, start_date=trip_results[0][2], end_date=trip_results[0][3])

@app.route("/payment_register",methods=["POST","GET"])
def payment_register():
    if request.method == "POST":
        price = request.form.get("price")
        place = request.form.get("place")
        event_name = request.form.get("event_name")
        user_name = request.form.get("user_name")

        #userが複数人いる場合は何度もやらなければならない
        #for in:
        cur.execute("SELECT * FROM user WHERE user_name = %s;",(user_name,))
        user_results = cur.fetchall()

        #cur.execute("INSERT INTO payment (trip_id, price, place, event_name) VALUES (%s,%s,%s,%s);", (session["trip_id"], price, place, event_name))
        #conn.commit()

        cur.execute("SELECT * FROM payment WHERE event_name = %s AND place = %s AND price = %s;",(event_name, place, price))
        trip_results = cur.fetchall()

        #cur.execute("INSERT INTO payment_member (payment_id, user_id) VALUES (%s,%s);", (trip_results[0][0], user_results[0][0]))            
        #conn.commit()
        return render_template("travel.html",user_name=user_name, trip_results=trip_results) 
    else:
        return render_template("payment_register.html")

@app.route("/payment_details")
def payment_details():
    return render_template("payment_details.html")

@app.route("/liquidation")
def liquidation():
    return render_template("liquidation.html")

if __name__ == "__main__":
    app.run(debug=True)