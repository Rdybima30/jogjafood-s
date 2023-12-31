from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import jwt
from bson import ObjectId
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename
import os
from os.path import join, dirname
from dotenv import load_dotenv


SECRET_KEY = "SPARTA"

# MONGODB_CONNECTION_STRING = "mongodb+srv://nadaanis526:nada2626anis@cluster0.zp4go5w.mongodb.net/"
# client = MongoClient(MONGODB_CONNECTION_STRING)
# db = client.jogjafood

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app=Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = './static/posting'

SECRET_KEY = 'secret1141'
TOKEN_KEY = 'mytoken'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/homepage")
def homepage():
    return render_template("homepage.html")

@app.route("/home")
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive,
                 SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"id": payload["id"]})
        return render_template("homepage.html",
            nickname=user_info["id"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("homepage",
            msg="Your login token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("homepage",
            msg="There was an issue logging you in"))
    
@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]
    email_give = request.form["email_give"]

    existing_user = db.user.find_one({"id": id_receive})
    if existing_user:
        return jsonify({"result": "fail", "msg": f"An acount with id '{id_receive}' is already. Please Login!"})

    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

    db.user.insert_one({
        "id": id_receive,
        "pw": pw_hash,
        "email": email_give
    })

    return jsonify({"result": "success"})

@app.route("/api/login", methods=["POST"])
def api_login():
    id_receive = request.form["id_give"]
    pw_receive = request.form["pw_give"]
    pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()
    result = db.user.find_one({"id": id_receive, "pw": pw_hash})
    if result is not None:
        payload = {
            "id": id_receive,
            "exp": datetime.utcnow() + timedelta(seconds=5),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"result": "success", "token": token})
    else:
        return jsonify({"result": "fail", "msg": "Either your email or your password is incorrect"})

    
@app.route("/api/id", methods=["GET"])
def api_valid():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        print(payload)
        userinfo = db.user.find_one({
            "id": payload["id"]},
            {"_id": 0}
        )
        return jsonify({
            "result": "success",
            "nickname": userinfo["id"]}
            )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return jsonify({
            "result": "fail",
            "msg": msg}
            )
    except jwt.exceptions.DecodeError:
        msg = "There was an error while logging you in"
        return jsonify({
            "result": "fail",
            "msg": msg}
        )

@app.route("/addmenu")
def addmenu():
    return render_template("addmenu.html")

@app.route("/formaddmenu")
def formaddmenu():
    return render_template("form_add_menu.html")

@app.route('/posting', methods=['POST'])
def posting():
    # sample_receive = request.form.get('sample_give')
    # print(sample_receive)
    # judul_menu = db.menu.find_one({'judul': judul})
    judul = request.form.get('judul')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    harga = request.form.get('harga')
    lokasi = request.form.get('lokasi')
    
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
   
    file = request.files["image"]
    extension = file.filename.split('.')[-1] 
    filename = f'post-{mytime}.{extension}'
    save_to = f'static/posting/{filename}'
    file.save(save_to)


    doc = {
        'judul': judul,
        'file': filename,
        'kategori': kategori,
        'deskripsi': deskripsi,
        'harga': harga,
        'lokasi': lokasi
    }

    db.menu.insert_one(doc)
    return jsonify({'msg': 'Data was saved!!'})

@app.route('/showmenu', methods=['GET'])
def show_menu():
    # menu = list(db.menu.find({},{'_id': False}))
    # return jsonify({'menu': menu})
    menu = db.menu.find()
    menu_list = []
    for attraction in menu:
        menu_list.append({
            'id': str(attraction['_id']),
            'judul': attraction['judul'],
            'kategori': attraction['kategori'],
            'deskripsi': attraction['deskripsi'],
            'image': attraction['file'],
            'harga': attraction['harga'],
            'lokasi': attraction['lokasi']
        })
    return jsonify(menu_list)

@app.route("/kategori")
def kategori():
    return render_template("kategori.html")

@app.route("/makanan")
def makanan():
    return render_template("makanan.html")

@app.route("/minuman")
def minuman():
    return render_template("minuman.html")

@app.route("/kategoriminuman")
def kategori_minuman():
    return render_template("kategori_minuman.html")

@app.route("/jajanan")
def jajanan():
    return render_template("jajanan.html")

@app.route("/kategorijajanan")
def kategori_jajanan():
    return render_template("kategori_jajanan.html")


@app.route("/detail_menu/<id>", methods=['GET'])
def detail_menu(id):
    menu = db.menu.find_one({'_id': ObjectId(id)})
    return render_template("detail_menu.html", menu = menu)

@app.route("/detail/<id>", methods=['GET'])
def detail(id):
    menu = db.menu.find_one({'_id': ObjectId(id)})
    return render_template("detail.html", menu = menu)

@app.route("/popular")
def popular():
    return render_template("popular.html")

@app.route("/edit/<id>", methods=['GET'])
def edit(id):
    menu = db.menu.find_one({'_id': ObjectId(id)})
    return render_template("edit.html", menu=menu)

@app.route('/update_menu/<id>', methods=['PUT'])
def update(id):
    judul = request.form.get('judul')
    deskripsi = request.form.get('deskripsi')
    lokasi = request.form.get('lokasi')
    harga = request.form.get('harga')
    kategori = int(request.form.get('kategori'))
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    # Get data lama dari database
    existing_menu = db.menu.find_one({'_id': ObjectId(id)})
    if existing_menu is None:
        return jsonify({'error': 'Menu not found'}), 404

    # Handle upload file baru
    file = request.files.get('file')
    if file:
        # Hapus file lama jika file dirubah
        if 'file' in existing_menu:
            existing_file_path = existing_menu['file']
            if os.path.exists(existing_file_path):
                os.remove(existing_file_path)

        extension = file.filename.split('.')[-1]
        filename = f'post-{mytime}.{extension}'
        save_to = f'static/posting/{filename}'
        file.save(save_to)

    else:
        # Menjaga file jika tidak ada file baru
        filename = existing_menu.get('file')

    # Update data database
    db.menu.update_one(
        {'_id': ObjectId(id)}, {
            '$set': {
            'judul': judul,
            'file': filename,
            'kategori': kategori,
            'deskripsi': deskripsi,
            'harga': harga,
            'lokasi': lokasi
            }
        }
    )
    return jsonify({'msg': 'Menu was updated!'})

@app.route("/review")
def review():
    return render_template("review.html")

@app.route("/komentar", methods=["POST"])
def komentar():
        name = request.form["name"]
        comment = request.form["comment"]
        star = request.form["star"]
        date = request.form["date"]
        doc = {
            # "id": userinfo["id"],
            "name": name,
            "star": star,
            "comment": comment,
            "date": date
        }
        db.komentar.insert_one(doc)

        return jsonify({
            'result':'success',
            'msg':'komentar success'
        })

@app.route('/showkomentar', methods=['GET'])
def show_komentar():
    komentar = list(db.komentar.find({},{'_id': False}))
    return jsonify({'komentar': komentar})

@app.route("/homepageadmin")
def homepageadmin():
    return render_template("homepage_admin.html")

@app.route('/delete/<menu_id>', methods=['DELETE'])
def delete(menu_id):
    # existing_menu = db.menu.find_one({'_id': ObjectId(menu_id)})
    db.menu.delete_one(
        {'_id': ObjectId(menu_id)}) 
    return jsonify({'msg':'Deleted success'})

@app.route('/search', methods=['GET'])
def search():
    query_params = request.args
    search_query = query_params.get('q', '')

    menu = db.menu.find(
        {'name': {'$regex': search_query, '$options': 'i'}})

    menu_list = []
    for attraction in menu:
        menu_list.append({
            'id': str(attraction['_id']),
            'judul': attraction['judul'],
            'kategori': attraction['kategori'],
            'deskripsi': attraction['deskripsi'],
            'image': attraction['file'],
            'harga': attraction['harga'],
            'lokasi': attraction['lokasi']
        })

    return jsonify(menu_list)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)