# -*- coding: utf-8 -*-
from flask import Flask,render_template, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from tempfile import mkdtemp
import mysql.connector
from datetime import datetime, timedelta
import os
import re
import config as db
import function
from sqlalchemy import func

"""
conn = db.conn
cur=conn.cursor()

cur.execute("USE travel")
conn.commit()
"""

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
app.permanent_session_lifetime = timedelta(minutes=3)
Session(app)

UPLOAD_FOLDER = './static/image/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

@app.route("/")
def layout():
    return render_template("login.html", url="url")

@app.route("/top")
def top():
    try:
        trip_results = db.session.query(db.Trip.trip_name,db.Trip.trip_id).filter(db.Trip.trip_id.in_(db.session.query(db.Trip_join.trip_id).filter(db.Trip_join.user_id == session["user_id"]))).all()
        #cur.execute("SELECT * FROM user WHERE user_id = %s",(session["user_id"],))
        #user_results = cur.fetchall()
        return render_template("top.html", trip_results=trip_results)#user_results=user_results[0][3]
    except:
        return render_template("login.html")

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        user = db.User()
        user.user_id = request.form.get("email")
        user.user_name = request.form.get("user_name")
        user.password = generate_password_hash(request.form.get("password"))
        user.img_file = request.files['img_file']

        """
        if user.img_file:
            filename = secure_filename(img_file.filename)
            img_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img_file.save(img_url)

            img_url = img_url.lstrip('.')
            #cur.execute("INSERT INTO user (user_id, user_name, password, avatar_image) VALUES (%s,%s,%s,%s);", (user_id, user_name, password,img_url))
            #conn.commit()
        #else:
            #cur.execute("INSERT INTO user (user_id, user_name, password) VALUES (%s,%s,%s);", (user_id, user_name, password))
            #conn.commit()
        """
        db.session.add(user)
        db.session.commit()
        return render_template("login.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        try:
            user_id = request.form.get("user_id")

            user_password = db.session.query(db.User.password).filter(db.User.user_id == user_id).first()
            if check_password_hash(user_password.password, request.form.get("password")):
                session["user_id"] = user_id
                flash('You were successfully logged in')
                return redirect('/top')
            else:
                error = 'ユーザーID・パスワードが誤っています'
                return render_template("login.html", error=error)
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
    #try:
        if request.method == "POST":
            trip = db.Trip()
            trip.trip_name = request.form.get("trip_name")
            trip.start_date = request.form.get("start_date")
            trip.end_date = request.form.get("end_date")
            user_ids = []
            count = 0
            while request.form.get("user_id" + str(count)):
                user_ids.append(request.form.get("user_id" + str(count)))
                count+=1
            db.session.add(trip)
            db.session.commit()

            trip_results = db.session.query(db.Trip).filter(db.Trip.trip_name == trip.trip_name, db.Trip.start_date == trip.start_date, db.Trip.end_date == trip.end_date).first()

            trip_join = db.Trip_join()
            trip_join.trip_id = trip_results.trip_id
            trip_join.user_id = session["user_id"]
            db.session.add(trip_join)
            db.session.commit()

            for user_id in user_ids:
                othermem_trip_join = db.Trip_join()
                othermem_trip_join.trip_id = trip_results.trip_id
                othermem_trip_join.user_id = user_id
                db.session.add(othermem_trip_join)
                db.session.commit()

            user_id_and_name = db.session.query(db.User.user_id,db.User.user_name).filter(db.User.user_id.in_(db.session.query(db.Trip_join.user_id).filter(db.Trip_join.trip_id == trip_results.trip_id))).all()
            list_instance = function.Return_list()
            user_results = list_instance.list_user(user_id_and_name)

            payment_results=[0]
            return render_template("travel.html",user_results=user_results,trip_results=trip_results,payment_results=payment_results)
        else:
            return render_template("travel_register.html")
    #except:
        #return render_template("login.html")

@app.route("/travel/<int:trip_id>")
def travel(trip_id):
    trip_results = db.session.query(db.Trip).filter(db.Trip.trip_id == trip_id).first()

    list_instance = function.Return_list()
    payment_user_results = db.session.execute("SELECT * FROM payment JOIN payment_member USING(payment_id) JOIN user USING(user_id) WHERE trip_id = %s;" % (trip_id))
    payment_results = list_instance.list_payment(payment_user_results)

    user_id_and_name = db.session.query(db.User.user_id,db.User.user_name).filter(db.User.user_id.in_(db.session.query(db.Trip_join.user_id).filter(db.Trip_join.trip_id == trip_results.trip_id))).all()
    user_results = list_instance.list_user(user_id_and_name)

    return render_template("travel.html",user_results=user_results, trip_results=trip_results ,payment_results=payment_results)

@app.route("/payment_register/<int:trip_id>",methods=["POST","GET"])
def payment_register(trip_id):
    if request.method == "POST":
        payment = db.Payment()
        payment.trip_id = trip_id
        payment.price = re.sub(r"\D","", request.form.get("price"))
        payment.place = request.form.get("place")
        payment.event_name = request.form.get("event_name")
        user_name = request.form.get("user_name")
        #userが複数人いる場合は何度もやらなければならない
        #for in:
        pay_member_id = db.session.query(db.User.user_id).filter(db.User.user_name == user_name).first()
        db.session.add(payment)
        db.session.commit()
        trip_results = db.session.query(db.Trip).filter(db.Trip.trip_id == payment.trip_id).first()
        payment_result = db.session.query(db.Payment.payment_id).filter(db.Payment.trip_id == payment.trip_id, db.Payment.event_name == payment.event_name, db.Payment.place == payment.place, db.Payment.price == payment.price).first()

        payment_member = db.Payment_member()
        payment_member.payment_id = payment_result.payment_id
        payment_member.user_id = pay_member_id.user_id
        db.session.add(payment_member)
        db.session.commit()

        list_instance = function.Return_list()
        payment_user_results = db.session.execute("SELECT * FROM payment JOIN payment_member USING(payment_id) JOIN user USING(user_id) WHERE trip_id = %s;" % (payment.trip_id))
        payment_results = list_instance.list_payment(payment_user_results)

        user_id_and_name = db.session.query(db.User.user_id,db.User.user_name).filter(db.User.user_id.in_(db.session.query(db.Trip_join.user_id).filter(db.Trip_join.trip_id == trip_results.trip_id))).all()
        user_results = list_instance.list_user(user_id_and_name)

        return render_template("travel.html", user_results=user_results, trip_results=trip_results ,payment_results=payment_results)
    else:
        return render_template("payment_register.html",trip_id=trip_id)

@app.route("/payment_details/<int:payment_id>")
def payment_details(payment_id):
    payment_results = db.session.query(db.Payment).filter(db.Payment.payment_id == payment_id).first()
    user_name = db.session.query(db.User.user_name).filter(db.User.user_id.in_(db.session.query(db.Payment_member.user_id).filter(db.Payment_member.payment_id == payment_id))).first()

    return render_template("payment_details.html",payment_results=payment_results, user_name=user_name.user_name)

@app.route("/liquidation/<int:member_count>/<int:trip_id>",methods=["POST","GET"])
def liquidation(member_count, trip_id):
    try:
        settle = db.Settle()
        #member_trip_id = (request.form.get("member_trip_id")).split(',')
        #member_count = (member_trip_id[0]).lstrip('(')
        settle.trip_id = trip_id

        my_user_name = (db.session.query(db.User.user_name).filter(db.User.user_id == session["user_id"]).first()).user_name
        trip_member_results = db.session.query(db.Trip_join).filter(db.Trip_join.trip_id == settle.trip_id).all()
        sum_price = (db.session.query(func.sum(db.Payment.price).label("sum_price")).filter(db.Payment.trip_id == settle.trip_id ).first()).sum_price

        should_pay_total = int(sum_price)/int(member_count)
        result = {}
        member_count_minus = 0

        def dic_sort(dic):
            list = sorted(dic.items(), reverse=True, key=lambda x:x[1])
            dic.clear()
            dic.update(list)
            return dic

        for i in range(int(member_count)):
            pay_total = (db.session.query(func.ifnull(func.sum(db.Payment.price), 0).label("pay_total")).filter(db.Payment.trip_id == settle.trip_id, db.Payment.payment_id.in_(db.session.query(db.Payment_member.payment_id).filter(db.Payment_member.user_id == trip_member_results[i].user_id))).first()).pay_total
            result[trip_member_results[i].user_id] = int(pay_total) - int(should_pay_total)
            if int(pay_total) - int(should_pay_total) < 0:
                member_count_minus+=1

        result = dic_sort(result)

        #金額の分配
        settle_results = db.session.query(db.Settle).filter(db.Settle.trip_id == settle.trip_id).all()
        if settle_results == []:
            while  not (result[next(iter(result))] < 5 and result[next(iter(result))] >= 0):
                settle.get_user_id=next(iter(result))
                settle.pay_user_id=list(result)[-1]
                caluculation = result[settle.get_user_id] - abs(result[settle.pay_user_id])
                if caluculation > 0:
                    settle.total_price = abs(result[settle.pay_user_id])
                    db.session.add(settle)
                    db.session.commit()
                    result[settle.get_user_id] = caluculation
                    result[settle.pay_user_id] = 0

                elif caluculation == 0:
                    settle.total_price = abs(result[settle.pay_user_id])
                    db.session.add(settle)
                    db.session.commit()
                    result[settle.get_user_id] = 0
                    result[settle.pay_user_id] = 0

                else:
                    settle.total_price = result[settle.get_user_id]
                    db.session.add(settle)
                    db.session.commit()
                    result[settle.get_user_id] = 0
                    result[settle.pay_user_id] = caluculation

                result = dic_sort(result)

        pay_settle_results = db.session.query(db.User.user_name, db.Settle.total_price).join(db.Settle, db.Settle.get_user_id == db.User.user_id).filter(db.Settle.trip_id == settle.trip_id, db.Settle.pay_user_id == session["user_id"]).all()
        get_settle_results = db.session.query(db.User.user_name, db.Settle.total_price).join(db.Settle, db.Settle.pay_user_id == db.User.user_id).filter(db.Settle.trip_id == settle.trip_id, db.Settle.get_user_id == session["user_id"]).all()

        return render_template("liquidation.html",my_user_name=my_user_name, get_settle_results=get_settle_results,pay_settle_results=pay_settle_results)
    except:
        return render_template("travel.html")

if __name__ == "__main__":
    app.run(debug=True)
