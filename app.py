# -*- coding: utf-8 -*-
from flask import Flask,render_template, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from tempfile import mkdtemp
import mysql.connector
from datetime import datetime, timedelta
import os



conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='****'
)

cur=conn.cursor()

cur.execute("USE travel")
conn.commit()


app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.permanent_session_lifetime = timedelta(minutes=3)
Session(app)

UPLOAD_FOLDER = './static/image/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def layout():
    return render_template("login.html", url="url")

@app.route("/top")
def top():
    try:
        cur.execute("SELECT * FROM trip WHERE trip_id IN (SELECT trip_id FROM trip_join WHERE user_id = %s)",(session["user_id"],))
        trip_results = cur.fetchall()

        #cur.execute("SELECT * FROM user WHERE user_id = %s",(session["user_id"],))
        #user_results = cur.fetchall()
        return render_template("top.html", trip_results=trip_results)#user_results=user_results[0][3]
    except:
        return render_template("login.html")

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        user_id = request.form.get("email")
        user_name = request.form.get("user_name")
        password = generate_password_hash(request.form.get("password"))
        img_file = request.files['img_file']

        if img_file:
            filename = secure_filename(img_file.filename)
            img_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img_file.save(img_url)
            
            img_url = img_url.lstrip('.')
            cur.execute("INSERT INTO user (user_id, user_name, password, avatar_image) VALUES (%s,%s,%s,%s);", (user_id, user_name, password,img_url))
            conn.commit()
        else:
            cur.execute("INSERT INTO user (user_id, user_name, password) VALUES (%s,%s,%s);", (user_id, user_name, password))
            conn.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        try:
            user_id = request.form.get("user_id")
            cur.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
            user_results = cur.fetchall()

            if check_password_hash(user_results[0][2], request.form.get("password")):
                session["user_id"] = user_id
                return redirect("/top")
            else:
                return render_template("login.html")
        except:
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return render_template("login.html")


@app.route("/travel_register",methods=["POST","GET"])
def travel_register():
    try:
        if request.method == "POST":
            trip_name = request.form.get("trip_name")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            user_ids = []
            count = 0
            while request.form.get("user_id" + str(count)):
                user_ids.append(request.form.get("user_id" + str(count)))
                count+=1
            
            #開始日を取得
            start = datetime.strptime(start_date, '%Y-%m-%d')
            #終了日を取得
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            cur.execute("INSERT INTO trip (trip_name, start_date, end_date) VALUES (%s,%s,%s);", (trip_name, start_date, end_date))
            conn.commit()

            cur.execute("SELECT * FROM trip WHERE trip_name = %s;",(trip_name,))
            trip_results = cur.fetchall()

            cur.execute("INSERT INTO trip_join (trip_id, user_id) VALUES (%s,%s);", (trip_results[0][0], session["user_id"]))
            conn.commit()

            for user_id in user_ids:
                cur.execute("INSERT INTO trip_join (trip_id, user_id) VALUES (%s,%s);", (trip_results[0][0], user_id))
                conn.commit()
            
            cur.execute("SELECT * FROM user WHERE user_id IN (SELECT user_id FROM trip_join WHERE trip_id = %s);",(trip_results[0][0],))
            user_results = cur.fetchall()
            
            return render_template("travel.html",user_results=user_results,trip_results=trip_results)
        else:
            return render_template("travel_register.html")
    except:
        return render_template("login.html")

@app.route("/travel",methods=["POST","GET"])
def travel():
    trip_name = request.form.get("trip_name")
    cur.execute("SELECT * FROM trip WHERE trip_name = %s;",(trip_name,))
    trip_results = cur.fetchall()

    cur.execute("SELECT * FROM payment JOIN payment_member USING(payment_id) JOIN user USING(user_id) WHERE trip_id IN (SELECT trip_id FROM trip WHERE trip_name = %s);",(trip_name,))
    payment_results = cur.fetchall()

    cur.execute("SELECT * FROM user WHERE user_id IN (SELECT user_id FROM trip_join WHERE trip_id IN (SELECT trip_id FROM trip WHERE trip_name = %s))",(trip_name,))
    user_results = cur.fetchall()

    return render_template("travel.html",user_results=user_results, trip_results=trip_results ,payment_results=payment_results)

@app.route("/payment_register",methods=["POST","GET"])
def payment_register():
    if request.method == "POST":
        trip_id1 = request.form.get("trip_id1")
        trip_id = request.form.get("trip_id")
        price = request.form.get("price")
        place = request.form.get("place")
        event_name = request.form.get("event_name")
        user_name = request.form.get("user_name")

        if trip_id1:
            return render_template("payment_register.html",trip_id=trip_id1)
        #userが複数人いる場合は何度もやらなければならない
        #for in:
        cur.execute("SELECT * FROM user WHERE user_name = %s;",(user_name,))
        pay_member_results = cur.fetchall()

        cur.execute("INSERT INTO payment (trip_id, price, place, event_name) VALUES (%s,%s,%s,%s);", (trip_id, price, place, event_name))
        conn.commit()

        cur.execute("SELECT * FROM trip WHERE trip_id = %s;",(trip_id,))
        trip_results = cur.fetchall()

        cur.execute("SELECT * FROM payment WHERE trip_id = %s AND event_name = %s AND place = %s AND price = %s;",(trip_id, event_name, place, price))
        add_payment_results = cur.fetchall()

        cur.execute("INSERT INTO payment_member (payment_id, user_id) VALUES (%s,%s);", (add_payment_results[len(add_payment_results)-1][0], pay_member_results[0][0]))            
        conn.commit()

        cur.execute("SELECT * FROM payment JOIN payment_member USING(payment_id) JOIN user USING(user_id) WHERE trip_id = %s",(trip_id,))
        payment_results = cur.fetchall()

        cur.execute("SELECT * FROM user WHERE user_id IN (SELECT user_id FROM trip_join WHERE trip_id = %s)",(trip_id,))
        user_results = cur.fetchall()
        
        return render_template("travel.html", user_results=user_results, trip_results=trip_results ,payment_results=payment_results)
    else:
        return render_template("payment_register.html")

@app.route("/payment_details",methods=["POST","GET"])
def payment_details():
    payment_id = request.form.get("payment_id")
    cur.execute("SELECT * FROM payment WHERE payment_id = %s",(payment_id,))
    payment_results=cur.fetchall()

    cur.execute("SELECT * FROM user WHERE user_id IN (SELECT user_id FROM payment_member WHERE payment_id = %s)",(payment_id,))
    user_results=cur.fetchall()

    return render_template("payment_details.html",payment_results=payment_results, user_name=user_results[0][1])

@app.route("/liquidation",methods=["POST","GET"])
def liquidation():
    try:
        member_trip_id = (request.form.get("member_trip_id")).split(',')
        member_count = (member_trip_id[0]).lstrip('(')
        trip_id = (member_trip_id[1]).strip(')  ')
        cur.execute("SELECT * FROM user WHERE user_id = %s",(session["user_id"],))
        my_user_name=(cur.fetchall())[0][1]

        cur.execute("SELECT * FROM trip_join WHERE trip_id = %s",(trip_id,))
        trip_member_results=cur.fetchall()

        cur.execute("SELECT SUM(price) FROM payment WHERE trip_id = %s;",(trip_id,))
        should_pay_total = int((cur.fetchall())[0][0])/int(member_count)
        result = {}
        member_count_minus = 0

        def dic_sort(dic):
            list = sorted(dic.items(), reverse=True, key=lambda x:x[1])
            dic.clear()
            dic.update(list)
            return dic

        for i in range(int(member_count)):
            cur.execute("SELECT IFNULL(SUM(price), 0) FROM payment WHERE trip_id = %s AND payment_id IN (SELECT payment_id FROM payment_member WHERE user_id = %s);",(trip_id,trip_member_results[i][2]))
            pay_total = (cur.fetchall())[0][0]
            
            result[trip_member_results[i][2]] = int(pay_total) - int(should_pay_total)
            if int(pay_total) - int(should_pay_total) < 0:
                member_count_minus+=1

        result = dic_sort(result)

        #金額の分配
        cur.execute("SELECT * FROM settle WHERE trip_id = %s", (trip_id,))
        settle_results=cur.fetchall()
        if settle_results == []: 
            while  not (result[next(iter(result))] < 5 and result[next(iter(result))] >= 0):
                first=next(iter(result))
                end=next(iter(reversed(result)))
                caluculation = result[first] - abs(result[end])
                if caluculation > 0:
                    cur.execute("INSERT INTO settle (trip_id, pay_user_id, get_user_id, total_price) VALUES (%s,%s,%s,%s);", (trip_id, end, first, abs(result[end])))            
                    conn.commit()
                    result[first] = caluculation
                    result[end] = 0
                    
                elif caluculation == 0:
                    cur.execute("INSERT INTO settle (trip_id, pay_user_id, get_user_id, total_price) VALUES (%s,%s,%s,%s);", (trip_id, end, first, abs(result[end])))            
                    conn.commit()
                    result[first] = 0
                    result[end] = 0
                    
                else: 
                    cur.execute("INSERT INTO settle (trip_id, pay_user_id, get_user_id, total_price) VALUES (%s,%s,%s,%s);", (trip_id, end, first, result[first]))            
                    conn.commit()
                    result[first] = 0
                    result[end] = caluculation
                
                result = dic_sort(result)

        cur.execute("SELECT user_name, total_price FROM settle JOIN user ON settle.get_user_id = user.user_id WHERE trip_id = %s AND pay_user_id = %s", (trip_id, session["user_id"]))
        pay_settle_results=cur.fetchall()

        cur.execute("SELECT user_name, total_price FROM settle JOIN user ON settle.pay_user_id = user.user_id WHERE trip_id = %s AND get_user_id = %s", (trip_id, session["user_id"]))
        get_settle_results=cur.fetchall()

        return render_template("liquidation.html",my_user_name=my_user_name, get_settle_results=get_settle_results,pay_settle_results=pay_settle_results)
    except:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)