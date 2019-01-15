from flask import Flask, render_template, request, url_for, redirect
import os
import re
import sqlite3
from cryptography.fernet import Fernet
from passlib.hash import sha256_crypt
app = Flask(__name__)

#email id validation
def is_email_address_valid(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z]+.([a-zA-Z]+)*$", email):
        return False
    return True

#file id validation
def file_id_valid(fileid):
    if re.match("^[0-9]",fileid):
        return True
    return False

# -- Main Index Page --
@app.route("/index/")
@app.route("/")
def index():
    return render_template('index.html')

# -- New User Page
@app.route("/new/")
def new():
    return render_template('new.html')

# -- Login Page
@app.route("/registered/login/")
def login():
    return render_template('login.html')

@app.route('/registered/login_display/', methods = ['POST'])
def login_display():
    errors = ''
    userid = request.form['userid'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()

    if not userid or not password:
        errors = 'Please enter all the values'
    if not errors:
        if not is_email_address_valid(email):
            errors = errors + "Please enter a valid email address"
    if not errors:
        data = {'userid': userid,
                'email': email,
                'password': password}
        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT COUNT(*) FROM USER WHERE USERID = ? AND EMAIL = ? AND PASSWORD = ?",(userid,email,password))
                for r in t:
                    u = r[0]

                if u >= 1:
                    msg = 'SUCCESSFULLY LOGGED IN'
                    print "\n"
                    print msg
                    print "\n"
                    return redirect(url_for('registered_file'))
                else:
                    errors = errors + "YOU NEED TO REGISTER FIRST, GO TO NEW USER PAGE"
                    return render_template('login.html', errors = errors)
        except:
            msg = "UNSUCCESSFUL LOGIN OPERATION"
            print "\n"
            print msg
            print "\n"
    return render_template('login.html', errors = errors)

# -- New File page --
@app.route('/new/new_file/')
def new_file():
    return render_template('new_file.html')

@app.route('/new/new_file_display/', methods = ['POST'])
def new_file_display():
    errors = ''
    userid = request.form['userid'].strip()
    username = request.form['username'].strip()
    fileid = request.form['fileid'].strip()
    filename = request.form['filename'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()

    if not userid or not username or not fileid or not filename or not password:
        errors = 'Please enter all the values'
    if not errors:
        if len(userid) > 20 or len(username) > 20 or len(filename) > 20 or len(str(fileid)) > 20:
            errors = errors + 'PLEASE ENTER VALUES LESS THAN 20 CHARACTERS / DIGITS'
    if not errors:
        if not is_email_address_valid(email):
            errors = errors + "PLEASE ENTER A VALID EMAIL ADDRESS"
    if not errors:
        if not file_id_valid(fileid):
            errors = errors + 'FILEID MUST BE OF INTEGER FORMAT'
    if not errors:

        key = " "
        token = " "
        value1 =  "Hello User, Your details are: \n USERID : " + str(userid) + "\n USERNAME : " + str(username) + "\n EMAIL : " + str(email) + "\n PASSWORD : " + str(password) + "."
        value2 = """\n\n\tOnce you are done with the 'New User Registration Process' you are redirected to the 'Registered users Page' and your data is saved
                    safely in the vaults. you can access you files through registered users page. you just need to enter 'User-ID', 'Email' and 'Password'.
                    with every updates and changes in the application, You will be notified via your Email. So please enter a valid email id.
                                                                            Thank you!"""
        value = value1 + value2
        filename = filename + "_" + username + "_config"

        f0 = open(filename,"wb")
        f0.write(value)
        f0.close()
        msg = 'SUCCESSFULLY CREATED FILE AND UPDATED DATA'
        print "\n"
        print msg
        print "\n"

        key = Fernet.generate_key()
        msg = 'KEY GENERATED SUCCESSFULLY'
        print msg
        f = Fernet(key)
        token = f.encrypt(value)
        msg = 'TOKEN GENERATED SUCCESSFULLY'
        print msg

        f5 = open(filename,"wb")
        f5.write(token)
        f5.close()
        msg = 'TOKEN WRITTEN TO FILE SUCCESSFULLY'
        print msg

        data = {'userid': userid,
                'username': username,
                'fileid': fileid,
                'filename': filename,
                'email': email,
                'password': password}

        #database connectivity and operation
        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT COUNT(*) FROM USER WHERE USERID = ?",(userid,))
                for r in t:
                    u = r[0]
                    error1 = "USERID ALREADY TAKEN PLEASE ENTER A DIFFERENT USERID"

                v = conn.execute("SELECT COUNT(*) FROM USER WHERE FILEID = ?",(fileid,))
                for r1 in v:
                    a = r1[0]
                    error2 = "FILEID ALREADY TAKEN PLEASE ENTER A DIFFERENT FILEID"

                if u >= 1:
                    errors = errors + error1
                    return render_template('new_file.html', errors = errors)
                elif a >= 1:
                    errors = errors + error2
                    return render_template('new_file.html', errors = errors)
                else:
                    conn.execute("INSERT INTO USER (USERID,USERNAME,FILEID,FILENAME,KEY,EMAIL,TOKEN,PASSWORD,VALUE) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",(userid,username,fileid,filename,key,email,token,password,value))
                    conn.commit()
                    msg = "RECORD ADDED SUCCESSFULLY"
                    print "\n"
                    print msg
                    print "\n"
                    return redirect(url_for('registered_file'))
        except:
            conn.rollback()
            msg = "ERROR IN INSERT OPERATION"
            print "\n"
            print msg
            print "\n"
    return render_template('new_file.html', errors = errors)

# -- Register Page --
@app.route('/registered/')
def registered():
    return render_template('registered.html')

# -- Registered Options Page --
@app.route('/registered/login/registered_file/')
def registered_file():
    return render_template('registered_file.html')

# -- successfull --
# -- Overwrite Data Page --
@app.route('/registered/login/registered_file/overwrite/')
def overwrite():
    return render_template('overwrite.html')

@app.route('/registered/login/registered_file/overwrite_display/', methods = ['POST'])
def overwrite_display():
    errors = ''
    fileid = request.form['fileid'].strip()
    newdata = request.form['newdata'].strip()

    if not fileid or not newdata:
        errors = 'PLEASE ENTER ALL THE VALUES (FILEID, DATA)'
        return render_template('overwrite.html', errors = errors)
    if not errors:
        token = " "
        o_key = " "
        data = {'fileid': fileid,
                'newdata': newdata}
        try:
            with sqlite3.connect('database.db') as conn:
                temp = conn.execute("SELECT FILENAME FROM USER WHERE FILEID = ?",(fileid,))
                for r1 in temp:
                    fname = r1[0]

                if len(fname) >= 1:
                    f0 = open(fname,'wb')
                    f0.write(newdata)
                    f0.close()
                    msg = 'DATA UPDATED'
                    print msg

                    newdata = str(newdata)
                    o_key = Fernet.generate_key()
                    f = Fernet(o_key)
                    token = f.encrypt(newdata)
                    msg = 'KEY AND TOKEN GENERATED'
                    print msg

                    f1 = open(fname,'wb')
                    f1.write(token)
                    f1.close()
                    msg = 'DATA ENCRYPTED'
                else:
                    errors = errors + 'FILEID NOT FOUND, PLEASE ENTER A VALID FILEID'
                    return render_template('overwrite.html', errors = errors)
        except:
            errors = errors + 'FILEID NOT FOUND, PLEASE ENTER A VALID FILEID'
            return render_template('overwrite.html', errors = errors)

        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT count(*) FROM USER WHERE FILEID = ?",(fileid,))
                for r in t:
                    u = r[0]

                if u == 1:
                    conn.execute("UPDATE USER set TOKEN = ? WHERE FILEID = ?",(token,fileid,))
                    conn.execute("UPDATE USER set VALUE = ? WHERE FILEID = ?",(newdata,fileid,))
                    conn.execute("UPDATE USER set KEY = ? WHERE FILEID = ?",(o_key,fileid,))
                    conn.commit()
                    msg = "FILE ID FOUND AND UPDATED"
                    print "\n"
                    print msg
                    print "\n"
                    message = 'OVERWRITE OPERATION SUCCESSFULL'
                    return render_template('overwrite_display.html', data = data, message = message)
                else:
                    errors = "ENTER VALID FILEID"
                    return render_template('overwrite.html', errors = errors)
        except:
            conn.rollback()
            msg = "UNSUCCESSFUL OPERATION"
            print "\n"
            print msg
            print "\n"
        return render_template('overwrite.html', errors = errors)

#-- successfull
# -- Append Data Page --
@app.route('/registered/login/registered_file/append/')
def append():
    return render_template('append.html')

@app.route('/registered/login/registered_file/append_display/', methods = ['POST'])
def append_display():
    errors = ''
    fileid = request.form['fileid'].strip()
    appenddata = request.form['appenddata'].strip()

    if not fileid or not appenddata:
        errors = 'PLEASE ENTER ALL THE VALUES (FILEID, DATA)'
        return render_template('append.html', errors = errors)
    if not errors:
        token = " "
        a_key = " "
        data = {'fileid': fileid,
                'appenddata': appenddata}

        try:
            with sqlite3.connect('database.db') as conn:
                od = conn.execute("SELECT VALUE FROM USER WHERE FILEID = ?",(fileid,))
                for r in od:
                    old_data = r[0]
                    space = " "
                    appenddata = str(old_data) + str(space) + str(appenddata)

                temp = conn.execute("SELECT FILENAME FROM USER WHERE FILEID = ?",(fileid,))
                for r1 in temp:
                    fname = r1[0]

                if len(fname) >= 1:
                    f0 = open(fname,'wb')
                    f0.write(appenddata)
                    f0.close()
                    msg = 'DATA UPDATED'
                    print msg

                    appenddata = str(appenddata)
                    a_key = Fernet.generate_key()
                    f = Fernet(a_key)
                    token = f.encrypt(appenddata)
                    msg = 'KEY AND TOKEN GENERATED'
                    print msg

                    f1 = open(fname,'wb')
                    f1.write(token)
                    f1.close()
                    msg = 'DATA ENCRYPTED'
                else:
                    errors = errors + 'FILEID NOT FOUND, PLEASE ENTER A VALID FILEID'
                    return render_template('append.html', errors = errors)
        except:
            errors = errors + 'FILEID NOT FOUND, PLEASE ENTER A VALID FILEID'
            return render_template('append.html', errors = errors)

        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT COUNT(*) FROM USER WHERE FILEID = ?",(fileid,))
                for r in t:
                    u = r[0]

                if u == 1:
                    conn.execute("UPDATE USER set VALUE = ? WHERE FILEID = ?",(appenddata,fileid))
                    conn.execute("UPDATE USER set KEY = ? WHERE FILEID = ?",(a_key,fileid))
                    conn.commit()
                    msg = "FILE ID FOUND AND UPDATED"
                    print "\n"
                    print msg
                    print "\n"
                    message = "APPEND OPERATION SUCCESSFULL"
                    return render_template('append_display.html', data = data, message = message)
                else:
                    errors = "ENTER VALID FILEID"
                    return render_template('append.html', errors = errors)
        except:
            conn.rollback()
            msg = "UNSUCCESSFUL OPERATION"
            print "\n"
            print msg
            print "\n"
        return render_template('append.html', errors = errors)

#-- successfull
# -- Decrypt Data Page --
@app.route('/registered/login/registered_file/decrypt/')
def decrypt():
    return render_template('decrypt.html')

@app.route('/registered/login/registered_file/decrypt_display/', methods = ['POST'])
def decrypt_display():
    errors = ''
    fileid = request.form['fileid'].strip()
    filename = request.form['filename'].strip()

    if not fileid or not filename:
        errors = 'PLEASE ENTER ALL THE VALUES (FILEID, FILENAME)'
        return render_template('decrypt.html', errors = errors)
    if not errors:
        data = {'fileid': fileid,
                'filename': filename}
        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT VALUE,TOKEN FROM USER WHERE FILEID = ? AND FILENAME = ?",(fileid,filename,))
                for r in t:
                    value = r[0]
                    token = r[1]
                    print value
                    print token
                    value = value + '\n\n' + token

                if len(value) >= 1:
                    msg = 'FILE FOUND'
                    print "\n"
                    print msg
                    print "\n"
                    message = 'DECRYPTION OPERATION SUCCESSFULL'
                    return render_template('decrypt_display.html', data = data, value = value, token = token, message = message)
                else:
                    errors = errors + "FILE NOT FOUND, PLEASE TRY AGAIN"
                    return render_template('decrypt.html', errors = errors)
        except:
            msg = "UNSUCCESSFUL LOGIN OPERATION"
            print "\n"
            print msg
            print "\n"
            errors = errors + 'FILEID NOT FOUND'
    return render_template('decrypt.html', errors = errors)

# -- successfull --
# -- Registered User New File Page --
@app.route('/registered/login/registered_file/reg_newfile/')
def reg_newfile():
    return render_template('reg_newfile.html')

@app.route('/registered/login/registered_file/reg_newfile_display/', methods = ['POST'])
def reg_newfile_display():
    errors = ''
    userid = request.form['userid'].strip()
    fileid = request.form['fileid'].strip()
    filename = request.form['filename'].strip()
    new_data = request.form['new_data'].strip()

    if not filename or not fileid or not userid:
        errors = 'PLEASE ENTER ALL THE VALUES'
    if not errors:
        if len(filename) > 20 or len(str(fileid)) > 20:
            errors = errors + 'PLEASE ENTER VALUES LESS THAN 20 CHARACTERS / DIGITS'
    if not errors:
        if not file_id_valid(fileid):
            errors = errors + 'FILEID MUST BE OF INTEGER FORMAT'
    if not errors:
        data = {'userid': userid,
                'fileid': fileid,
                'filename': filename,
                'new_data': new_data}
        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT COUNT(*) FROM USER WHERE USERID = ?",(userid,))
                for r in t:
                    u  = r[0]
                if u >= 1:
                    f0 = open(filename,'wb')
                    f0.write(new_data)
                    f0.close()
                    msg = 'DATA UPDATED'
                    print msg

                    new_data = str(new_data)
                    n_key = Fernet.generate_key()
                    f = Fernet(n_key)
                    n_token = f.encrypt(new_data)
                    msg = 'KEY AND TOKEN GENERATED'
                    print msg

                    f1 = open(filename,'wb')
                    f1.write(n_token)
                    f1.close()
                    msg = 'DATA ENCRYPTED'
                else:
                    errors = errors + 'FILEID NOT FOUND, PLEASE ENTER A VALID FILEID'
                    return render_template('reg_newfile.html', errors = errors)
        except:
            errors = errors + 'FILEID NOT FOUND, PLEASE ENTER A VALID FILEID'
            return render_template('reg_newfile.html', errors = errors)

        try:
            with sqlite3.connect('database.db') as conn:
                t = conn.execute("SELECT COUNT(*) FROM USER WHERE USERID = ?",(userid,))
                for r in t:
                    u  = r[0]
                if u >= 1:
                    msg = "USERID FOUND"
                    print "\n"
                    print msg
                    print "\n"
                    v = conn.execute("SELECT * FROM USER WHERE USERID = ?",(userid,))
                    for r1 in v:
                        uid = r1[0]
                        uname = r1[1]
                        fid = fileid #r1[2]
                        fname = filename #r1[3]
                        key = n_key #r1[4]
                        email = r1[5]
                        token = n_token #r1[6]
                        password = r1[7]
                        value = new_data
                    conn.execute("INSERT INTO USER (USERID,USERNAME,FILEID,FILENAME,KEY,EMAIL,TOKEN,PASSWORD,VALUE) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9)",(uid,uname,fid,fname,key,email,token,password,value))
                    conn.commit()
                    msg = "RECORD ADDED SUCCESSFULLY"
                    print "\n"
                    print msg
                    print "\n"
                    message = 'NEW FILE CREATED SUCCESSFULLY'
                    return render_template('reg_newfile_display.html', data = data, message = message)
                else:
                    errors = errors + "USER ID NOT FOUND PLEASE ENTER A VALID ID"
                    return render_template('reg_newfile.html', errors = errors)
        except:
            conn.rollback()
            msg = "ERROR IN INSERT OPERATION"
            print "\n"
            print msg
            print "\n"
    return render_template('reg_newfile.html', errors = errors)

@app.route('/registered/login/registered_file/delete/')
def delete():
    return render_template('delete.html')

@app.route('/registered/login/registered_file/delete_display/', methods = ['POST'])
def delete_display():
    errors = ''
    userid = request.form['userid'].strip()
    fileid = request.form['fileid'].strip()
    data = {'userid' : userid,
            'fileid' : fileid}
    if not userid or not fileid:
        errors = 'PLEASE ENTER ALL THE VALUES (USERID, FILEID)'
        return render_template('delete.html', errors = errors)
    if not errors:
        data = {'userid': userid,
                'fileid': fileid}
        try:
            with sqlite3.connect('database.db') as conn:
                conn.execute("DELETE FROM USER WHERE FILEID = ?",(fileid,))
                conn.commit()
                message = 'FILE DELETION SUCCESSFULL'
                return render_template('delete_display.html', message = message)
        except:
            msg = "FILE NOT FOUND"
            print "\n"
            print msg
            print "\n"
            errors = errors + 'FILE NOT FOUND, EITHER DELETED OR NOT CREATED'
    return render_template('delete.html', errors = errors)

@app.route('/registered/login/registered_file/user/')
def user():
    return render_template('user.html')

@app.route('/registered/login/registered_file/user_display/', methods = ['POST'])
def user_display():
    fileid = list()
    filename = list()
    errors = ''
    userid = request.form['userid'].strip()

    if not userid:
        errors = 'PLEASE ENTER USERID'
    if not errors:
        data = {'userid' : userid}
        try:
            with sqlite3.connect('database.db') as conn:
                c = conn.execute("SELECT * FROM U_VIEW WHERE USERID = ?",(userid,))
                for t in c:
                    #uid = t[0]
                    uname = t[1]
                    email = t[2]
                cursor = conn.execute("SELECT * FROM USER_VIEW WHERE USERID = ?",(userid,))
                for k in cursor:
                    uid = k[0]
                    fid = k[1]
                    fileid.append(fid)
                    fname = k[2]
                    filename.append(fname)
                msg = "USER FOUND AND RETREIVED"
                print msg
                message = 'WELCOME USER' + uname.upper()
                return render_template('user_display.html',uid = uid, uname = uname, fileid = fileid, filename = filename, email = email, message = message)
        except:
            msg = "USERID NOT FOUND"
            print msg
            errors = errors + 'USERID NOT FOUND, PLEASE ENTER A VALID ID'
    return render_template('user.html', errors = errors)

# -- Error Handler 404 Page --
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html')

@app.errorhandler(405)
def page_not_found(e):
    return render_template('error_405.html')

# -- Application Run File --
if __name__ == '__main__':
    app.run(debug = True)
