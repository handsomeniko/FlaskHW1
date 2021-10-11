import re, sqlite3
from flask import Flask, render_template, url_for, request ,make_response,redirect
import pandas as pd
import time

app = Flask(__name__)

def register_action():
    username = request.form.get('username', '')
    email = request.form.get('email', '')
    password1 = request.form.get('password1', '')
    password2 = request.form.get('password2', '')

    if not username:
        return '請輸入username'
    elif not email:
        return '請輸入email'
    elif not password1:
        return '請輸入password'
    elif not password2:
        return '請輸入password'
    elif len(password1)<4:
        return '密碼必須大於4碼'
    elif not password1==password2:
        return '兩次密碼必須相符'

    con = sqlite3.connect('mywebsite.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE `email`="{email}"')
    queryresult = cur.fetchall()
    if queryresult:
        return 'email重複，請使用另一個email'
    cur.execute(f'SELECT * FROM user WHERE `username`="{username}"')
    queryresult = cur.fetchall()
    if queryresult:
        return 'username重複，請使用另一個usernme'
    # Insert a row of data
    cur.execute(f"INSERT INTO user (`username`, `email`, `password`) VALUES ('{username}','{email}','{password1}')")
    # Save (commit) the changes
    con.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()
    
    return '註冊成功'

def do_the_login():
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    con = sqlite3.connect('mywebsite.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE `email`="{email}"')
    queryresult1 = cur.fetchall()
    if not queryresult1:
        return '此email未註冊'
    df = pd.read_sql(f'SELECT * FROM user WHERE `email`="{email}"',con)
    if str(df['password'][0]) != str(password):
        return 'email或password錯誤'
    con.close()
    username=df['username'][0]
    email=df['email'][0]
    resp = make_response(render_template('user.html', username=username, email=email))
    value=username+','+email
    resp.set_cookie(key='cookie', value=value)
    return resp




@app.route('/')
def index():
    cookie_value = request.cookies.get('cookie')
    if cookie_value == None:
        return redirect(url_for('login'))
    else :
        username ,email= cookie_value.split(',')
        return render_template('index.html',username=username,email=email)


@app.route('/user/<username_type>')
def show_user_profile():
    cookie_value = request.cookies.get('cookie')
    if  cookie_value == None:
        return redirect(url_for('login'))
    else :
        username ,email= cookie_value.split(',')
        return render_template('user.html',username=username,email=email)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        # return request.form.get('username', '')+';'+request.form.get('email', '')
        return register_action()
    else:
        # username = request.args.get('username', '') if request.args.get('username', '') else ''
        username = request.args.get('username', '')
        email = request.args.get('email', '')
        return render_template('register.html', username=username, email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return render_template('login.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
