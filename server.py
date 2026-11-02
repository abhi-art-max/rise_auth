from flask import *
import bcrypt
import sqlite3
import uuid

app = Flask("restraunt")

@app.route('/api/signup', methods=['POST'])
def signup():
    conn = sqlite3.connect("restraunt.db")
    cur = conn.cursor()

    body = request.get_json()
    name = body["name"]
    password = body["password"]
    role = body["role"]
    if role.lower() == "chef" :
        conn.close()
        return jsonify({
            "error": "Your are not authorised for this role!!" 
        })

    bytesP = password.encode('utf-8')
    hashedP = bcrypt.hashpw(bytesP, bcrypt.gensalt())
    id = str(uuid.uuid4())

    response =  redirect('/')
    response.set_cookie(
        key="token",
        value=id ,
        httponly=True
    )

    cur.execute(
        "INSERT INTO users VALUES(?,?,?,?)",
        [id, name, hashedP, role]
    )
    cur.execute(
        "INSERT INTO sessions VALUES(?,?)",
        [id, id]
    )

    conn.commit()
    conn.close()

    return (response),302


@app.route('/api/login', methods=['POST'])
def login():
    conn = sqlite3.connect("restraunt.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    body = request.get_json()
    name = body['name']
    password = body['password']
    bPass = password.encode('utf-8')
                           
    cur.execute("SELECT * FROM users WHERE name = ?", [name])
    user = cur.fetchone()

    if not user:
        conn.close()
        return jsonify(
        {
            "status": "user does not exist"
        }), 404

    if not bcrypt.checkpw(bPass, user["password"]) :
        conn.close()
        return jsonify(
        {
            "status": "wrong password", 
        }), 401

    token = str(uuid.uuid4())

    response =  redirect('/')
    response.set_cookie(
        key="token" ,
        value=token ,
        httponly=True
    )
    cur.execute(
        "INSERT INTO sessions VALUES(?,?)",
        (token, user["id"])
    )

    conn.commit()
    conn.close()

    return (response),302

@app.route('/authPage')
def auth():
    return render_template('authPage.html')

@app.route('/', methods=["GET"])
def get_profile():
    conn = sqlite3.connect("restraunt.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    token = request.cookies.get("token")

    if not token:
        conn.close()
        return redirect('/authPage')

    cur.execute("SELECT * FROM sessions WHERE token = ?", [token])
    ssn = cur.fetchone()

    if not ssn:
        conn.close()
        return redirect('/authPage')

    cur.execute("SELECT * FROM users WHERE id = ?", [ssn["id"]])
    user = cur.fetchone()

    cur.execute("SELECT item FROM orders WHERE id = ?",[ssn["id"]])
    orders = [row['item'] for row in cur.fetchall()]

    conn.close()

    return render_template('homePage.html', name=user['name'], orders=orders, role=user['role'])

@app.route('/api/addItem', methods=['POST'])
def addItem():
    conn = sqlite3.connect("restraunt.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    token = request.cookies.get("token")
    cur.execute("SELECT id FROM sessions WHERE token = ?", [token])
    userid = cur.fetchone()["id"]
    print(userid)

    itemName = request.get_data().decode("utf-8")
    print(itemName)
    cur.execute(
        "INSERT INTO orders VALUES(?,?)", 
        [userid, itemName]
    )
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/api/logout')
def logout():
    response = redirect('/')
    response.delete_cookie("token")
    return response

app.run(port=5500, debug=True)



