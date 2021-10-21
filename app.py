# -*- coding: utf-8 -*-
from flask import Flask,render_template, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from tempfile import mkdtemp
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)

@app.route("/")
def layout():
    return render_template("layout.html", url="url")

@app.route("/top")
def top():
    return render_template("top.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/travel_register", methods =['POST', 'GET'])
def travel_register():
    if request.method == 'POST':
        #旅行日を取得
        trip = request.form['trip_name']
        #日付を取得
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        #開始日を取得
        start = datetime.strptime(start_date, '%Y-%m-%d')
        #終了日を取得
        end = datetime.strptime(end_date, '%Y-%m-%d')
    return render_template("travel_register.html")

@app.route("/travel")
def travel():
    return render_template("travel.html")

@app.route("/payment_register")
def payment_register():
    return render_template("payment_register.html")

@app.route("/payment_details")
def payment_details():
    return render_template("payment_details.html")

@app.route("/liquidation")
def liquidation():
    return render_template("liquidation.html")

#おまじない
if __name__ == "__main__":
    app.run(debug=True)