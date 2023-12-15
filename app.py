from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname
from dotenv import load_dotenv

app=Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = './static/profile_pics'

SECRET_KEY = "SPARTA"

MONGODB_CONNECTION_STRING = "mongodb+srv://nadaanis526:nada2626anis@cluster0.zp4go5w.mongodb.net/"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.jogjafood
users_collection = db['users']

SECRET_KEY = 'secret1141'
TOKEN_KEY = 'mytoken'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/home', methods=['GET'])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        print(user_info)
        return render_template('homepage.html', user_info=user_info, logged_in=logged_in, is_admin=is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('homepage.html', msg=msg)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/signup',methods=['POST'])
def api_register():
    name=request.form.get('name')
    email=request.form.get('email')
    password=request.form.get('password')

    pw_hash=hashlib.sha256(password.encode('utf-8')).hexdigest() #mengenskripsi pw

    db.user.insert_one({
        'name':name,
        'email':email,
        "category": 'visitor',
        'password':pw_hash
    })
    return  jsonify({'result':'success'})

@app.route('/login')
def login():
    return render_template('login.html')

@app.route("/signin", methods=["POST"])
def signin():
    email = request.form["email"]
    password = request.form["password"]
    print(email)
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print(pw_hash)
    result = db.users.find_one(
        {
            "email": email,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )
    


@app.route('/addmenu')
def add_menu():
    return render_template('addmenu.html')


@app.route('/detail')
def detail():
    return render_template('detail.html')


@app.route('/edit')
def edit():
    return render_template('edit.html')


@app.route('/formaddmenu')
def form_add_menu():
    return render_template('form_add_menu.html')


@app.route('/homepageadmin')
def homepage_admin():
    return render_template('homepage_admin.html')


@app.route('/kategori')
def kategori():
    return render_template('kategori.html')

@app.route('/popular')
def popular():
    return render_template('popular.html')

@app.route('/review')
def review():
    return render_template('review.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
