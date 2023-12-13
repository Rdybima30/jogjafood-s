from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname
from dotenv import load_dotenv

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/popular')
def popular():
    return render_template('popular.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/review')
def review():
    return render_template('review.html')


if __name__ == '__main__':
    app.run(debug=True)
