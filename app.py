
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

@app.route("/travel_register")
def travel_register():
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