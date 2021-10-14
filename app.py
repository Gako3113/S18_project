
#Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import Flask,render_template

#Flaskオブジェクトの生成
app = Flask(__name__)




@app.route("/")
def layout():
    return render_template("layout.html")



@app.route("/top")
def top():
    return render_template("top.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

#おまじない
if __name__ == "__main__":
    app.run(debug=True)