import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, url_for, redirect, request, session
# The Session instance is not used for direct access, you should always use flask.session
# import flask.sessions


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = "static/userdata/"


# Ensure templates are auto reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Main route
@app.route("/", methods=["GET", "POST"])
def home():
    if session.get("name"):
        return render_template("index.html") 
    else:
        return render_template("index.html")   
    

# Favicon
# Load Browser Favorite Icon
@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/AMTS_Logo.png')

# Services route
@app.route("/services", methods=["GET", "POST"])
def services():
    return render_template("services.html")

# about-us route
@app.route("/about_us", methods=["GET", "POST"])
def about_us():
    return render_template("about_us.html")

# contact-us route
@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    return render_template("contact_us.html")

# Login-page route
@app.route("/loginpage", methods=["GET", "POST"])
def loginpage():
    return render_template("loginpage.html")

# LoginFrom route
@app.route("/loginform", methods=["GET", "POST"])
def loginform():
    if request.method == "POST":
        conn = sqlite3.connect("passdetails.sql")
        db = conn.cursor()

        username = request.form.get("username")        
        password = request.form.get("password")

        sql = f"SELECT COUNT(username),password FROM userlogindetails WHERE username='{username}'"
        
        try:
            db.execute(sql)
            details = db.fetchone()
            if (details[0] == 0):
                return render_template("sorry.html", msg = "User Not Found")
            else:
                pswd = details[1]
                

            if ( check_password_hash(password=password, pwhash=pswd) ):
                session["name"] = username
                if session.get("name"):
                    return redirect("/dashboard")
            else:
                return render_template("sorry.html", msg="Enter valid username/password")
        
        except sqlite3.Error as e:
            print(e, details, "This is error")
            return render_template("sorry.html", msg="User Not Found")
    else:
        return render_template("index.html")
    
# Sign up route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")

# Sign up Form for first time
@app.route("/signupform", methods=["GET", "POST"])
def signupform():
    if request.method == "POST":
        conn = sqlite3.connect("passdetails.sql")
        db = conn.cursor()

        username = request.form.get("username")
        password = request.form.get("password")
        useremail = request.form.get("useremail")

        sql = f"SELECT COUNT(username) FROM userlogindetails WHERE username='{username}'"
        db.execute(sql)
        details = db.fetchone()
        if (details[0] == 1):
            return render_template("signup.html", msg="Username already taken.")

        password = generate_password_hash(password)
        query = f'INSERT INTO userlogindetails (username, password, useremail) VALUES("{username}", "{password}", "{useremail}")'
        
        try:
            db.execute(query)
            conn.commit()
            db.close()
            conn.close()
            return redirect("/")
            # return render_template("success.html", msg="You are registered successfully.")
        except:
            return render_template("sorry.html", msg="Try Again.")

    else:
        return render_template("signup.html")
    


#  Logout route
@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if session.get("name"):
        if request.method == "GET":
            conn = sqlite3.connect("passdetails.sql")
            db = conn.cursor()
            username = session["name"]
            sql = f"SELECT * FROM userdetails WHERE username='{username}'"
            print(sql)
            try:
                db.execute(sql)
                userdetails = db.fetchone()
                uname = userdetails[0]
                userimage = userdetails[4]
                # print(userimage)
                db.close()
                conn.close()
                # userimagelink = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(userimage))
                # print(userimagelink)
                # print(uname)
                return render_template("dashboard.html", uname = f"{uname}", image1 = userimage)
            except:
                # print("Hello dear!, haha")
                return render_template("dashboard.html")
        else:
            return render_template("dashboard.html")
    else:
        return render_template("sorry.html")
    

@app.route("/apply-pass", methods=["GET", "POST"])
def applypass():
    return render_template("passform.html")


@app.route("/passform", methods=["GET", "POST"])
def passform():
    if session.get("name"):
        if request.method == "POST":
            conn = sqlite3.connect("passdetails.sql")
            db = conn.cursor()

            name = request.form.get("userfullname")
            contactno = request.form.get("userphone", type=int)
            email = request.form.get("usermail")
            college = request.form.get("usercollege")
            username = session["name"]
            userimage = request.files["userimage"]
            userimage.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(userimage.filename)))
            # url = userimage.filename

            # userimage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            sql = f"INSERT INTO userdetails (name, contactno, email, college, userimage, username) VALUES ('{name}', {contactno}, '{email}', '{college}', '{userimage.filename}', '{username}')"
            print(sql)

            try:
                db.execute(sql)
                conn.commit()
                db.close()
                conn.close()
                return render_template("success.html", msg="You're request sent successfully.")
            
            except:
                return render_template("sorry.html", msg="Try Again.")

            # pass
        else:
            return render_template("dashboard.html")




if __name__ == "__main__":
    app.run(debug=True)


