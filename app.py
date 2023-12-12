import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for
)
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

TOKEN_KEY = 'kelompok3'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/kategori', methods=['GET'])
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            TOKEN_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user.find_one({"id": payload["id"]})
        return render_template(
            "index.html",
            nickname=user_info["nick"]
        )
    except jwt.ExpiredSignatureError:
        return redirect(url_for(
            "login",
            msg="Your login token has expired")
        )
    except jwt.exceptions.DecodeError:
        return redirect(url_for(
            "login",
            msg="There was an issue logging you in")
        )
@app.route('/login',methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html',msg=msg)

@app.route('/user/<username>',methods=['GET'])
def user(username):
    token_receive=request.cookies.get(TOKEN_KEY)
    try:

        payload = jwt.decode(
            token_receive,
            TOKEN_KEY,
            algorithms=['HS256']
        )
        status = username == payload.get('id')
        user_info = db.users.find_one(
            {'username':username},
            {'_id':False}
        )
        return render_template(
            'user.html',
            user_info = user_info,
            status = status
        )
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
   
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )

    if result:
        payload = {
            "id": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }

        # header = payload, signature = HS256
        token = jwt.encode(
            payload,
            TOKEN_KEY,
            algorithm="HS256"
        )

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

if __name__ == '__main__':
    app.run(debug=True)
