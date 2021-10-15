# -*- coding: utf-8 -*-
from flask import Flask,render_template, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector

conn = mysql.connector.connect(
    host= 'localhost',
    user= 'root',
    password='*****'
)

cur=conn.cursor()

cur.execute("USE travel")
conn.commit()

app = Flask(__name__)




@app.route("/")
def layout():
    return render_template("layout.html")



@app.route("/top")
def top():
    return render_template("top.html")

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        if not request.form.get("email"):
            return "メールアドレスを正しく入力してください"
        if not request.form.get("user_name"):
            return "ユーザー名を正しく入力してください"
        if not request.form.get("password"):
            return "パスワードを正しく入力してください"

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
        try:
            if not request.form.get("user_id") or not request.form.get("password"):
                return render_template("login.html")
                    
            cur.execute("SELECT * FROM user WHERE user_id = %s", (request.form.get("user_id"),))
            results = cur.fetchall()

            if check_password_hash(results[0][2], request.form.get("password")):
                return render_template("top.html")
            else:
                return render_template("login.html")
        except:
            return render_template("login.html")

    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)