from flask import Flask,render_template, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
import tkinter

conn = mysql.connector.connect(
    host= 'localhost',
    user= 'root',
    password='****'
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
            if tkinter.messagebox.showwarning(title="alert",message="メールアドレスを正しく入力してください") == "OK":
                return render_template("register.html")
        if not request.form.get("user_name"):
            if tkinter.messagebox.showwarning(title="alert",message="ユーザー名を正しく入力してください") == "OK":
                return render_template("register.html")
        if not request.form.get("password"):
            if tkinter.messagebox.showwarning(title="alert",message="パスワードを正しく入力してください") == "OK":
                return render_template("register.html")

        user_id = request.form.get("email")
        user_name = request.form.get("user_name")
        password = generate_password_hash(request.form.get("password"))

        cur.execute("INSERT INTO user (user_id, user_name, password) VALUES (?,?,?);", user_id, user_name, password)
        conn.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        if not request.form.get("user_id") or not request.form.get("password"):
            if tkinter.messagebox.showwarning(title="alert",message="ユーザーIDもしくはパスワードが誤っています") == "OK":
                return render_template("login.html")
                
        results = cur.execute("SELECT * FROM user WHERE user_id = ?", request.form.get("user_id"))
        conn.commit()
        if not check_password_hash(results[0]["password"], request.form.get("password")):
            return render_template("top.html")
        else:
            if tkinter.messagebox.showwarning(title="alert",message="パスワードを正しく入力してください") == "OK":
                return render_template("login.html")
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)