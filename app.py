#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 17:27:47 2024

@author: szymonkopycinski
"""
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify # type: ignore
from random import choice, randint
from databaseManager import checkCredentials, enter, fetchAllCreds, deleteUser
import os
from datetime import timedelta, datetime
import time
import threading
import uuid

app = Flask(__name__)


#app.secret_key = os.environ.get('SECRET_KEY')
app.secret_key = 'abcCHANGEME'

app.config.update(
    SESSION_COOKIE_SECURE=False,  # Send cookies only over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE='Lax',  # Protect against CSRF in some scenarios
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=60),  # Auto-expire sessions
)

login_verification_list_of_worded_numbers = [
    'one','two','three','four','five','six','seven','eight','nine','ten'
]

active_sessions = {}

# ----- pages 

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        userGroup = request.form.get("userGroup")
        verification_input = request.form.get("verification")

        # Retrieve stored session values
        verification_value_worded_number = session.get("verification_value_worded_number", 0)
        verification_second_number = session.get("verification_second_number", 0)
        correct_sum = verification_value_worded_number + verification_second_number

        if verification_input and verification_input.isdigit() and int(verification_input) == correct_sum:
            verification = True
        else:
            verification=False
            session.clear()
            session.modified = True  # Reset session on failure

        # Validate user credentials
        checkCredentialsQuery = checkCredentials(username, password, userGroup)

        if checkCredentialsQuery[0] and verification:
            session["logged_in"] = True
            session["userPermissionScope"] = checkCredentialsQuery[1]
            session.modified = True
            if userGroup == "other" and int(checkCredentialsQuery[1]) > 2:
                session["adminLoggedIn"] = True
                session.modified = True

            if "sid" not in session:
                session["sid"] = str(uuid.uuid4())
                session.modified = True

            active_sessions[session["sid"]] = {
                "username": username,
                "userGroup": userGroup,
                "login_time": datetime.now().strftime('%d/%m %H:%M:%S'),
                "permission_scope": checkCredentialsQuery[1]
            }

            return redirect(url_for("home"))
        else:
            flash("Log in failed, please try again")
            return redirect(url_for("index"))

    # For GET requests, generate a new verification question
    verification_worded_number = choice(login_verification_list_of_worded_numbers)
    verification_value_worded_number = login_verification_list_of_worded_numbers.index(verification_worded_number) + 1
    verification_second_number = randint(1, 10)

    # Store verification values in the session
    session["verification_value_worded_number"] = verification_value_worded_number
    session["verification_second_number"] = verification_second_number
    session["logged_in"] = False
    session.modified = True

    # Display verification numbers
    verification_list = [verification_worded_number, verification_second_number]
    return render_template("index.html", verification_list=verification_list, current_time=time.time())


@app.route("/home")
def home():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time())
        
        else:
            return render_template("home.html",admin=False, current_time=time.time())
    
    else:
        session.clear()
        return redirect(url_for("index"))

@app.route("/risk")
def risk():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time())
        
        else:
            return render_template("home.html",admin=False, current_time=time.time())
    
    else:
        session.clear()
        return redirect(url_for("index"))

@app.route("/performance")
def performance():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time())
        
        else:
            return render_template("home.html",admin=False, current_time=time.time())
    
    else:
        session.clear()
        return redirect(url_for("index"))

@app.route("/profile")
def profile():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time())
        
        else:
            return render_template("home.html",admin=False, current_time=time.time())
    
    else:
        session.clear()
        return redirect(url_for("index"))




@app.route("/admin")
def admin_panel():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            userCreds = fetchAllCreds()
            userScope = session.get("userPermissionScope")

            return render_template("admin_panel.html", userScope=userScope,active_sessions=active_sessions, session=session, userCreds=userCreds, current_time=time.time(), admin=True)
        
        else:
            session.clear()
            return redirect(url_for("index"))
    
    else:
        session.clear()
        return redirect(url_for("index"))
        

# ------ functions

@app.after_request
def add_cache_control(response):
    # Cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # Check if the session is empty or not logged in, and clean up active_sessions
    sid = session.get("sid")
    if not session.get("logged_in") and sid in active_sessions:
        active_sessions.pop(sid, None)  # Remove the user from active_sessions if their session is cleared

    if 'image' in response.content_type:
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 1 day
        response.headers["Expires"] = (datetime.utcnow() + timedelta(days=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response

@app.route("/terminate_session", methods=['POST'])
def terminate_session():
    if not session.get("adminLoggedIn") and session.get("sid") not in active_sessions:
        return redirect(url_for("index"))  # Ensure only admins can access this route
    
    sid = request.form.get("sid")  # Get the session ID from the form
    if sid and sid in active_sessions:
        user_data = active_sessions[sid]
        active_sessions.pop(sid, None)

        flash(f"{user_data['username']}")

    else:
        flash("Invalid SID, could not terminate")

    return redirect(url_for("admin_panel"))

@app.route("/delete_user", methods=['POST'])
def delete_user():
    if not session.get("adminLoggedIn") and session.get("sid") not in active_sessions:
        return redirect(url_for("index"))  # Ensure only admins can access this route
    
    if session.get("sid") in active_sessions:
        deleteUser(request.form.get("username"))

    return redirect(url_for("admin_panel"))

@app.route("/create_user", methods=['POST'])
def create_user():
    if not session.get("adminLoggedIn") and session.get("sid") not in active_sessions:
        return redirect(url_for("index"))  # Ensure only admins can access this route
    
    if session.get("sid") in active_sessions:
        username = request.form.get("username")
        fname = request.form.get("fname")
        passw = request.form.get("password")
        team = request.form.get("team")
        permission_scope = request.form.get("permission_scope")
        phone_number = request.form.get("phone_number")
        enter(username,fname,passw,team,phone_number,permission_scope)

    return redirect(url_for("admin_panel"))



@app.route("/create", methods=["GET","POST"])
def create():
    if request.method == "POST":
        username = request.form.get("username")
        fname = request.form.get("fname")
        password = request.form.get("password")
        phoneNumber = request.form.get("phoneNumber")
        userGroup = request.form.get("userGroup")

        enter(username,fname, password,userGroup,phoneNumber,"1")
        return redirect(url_for("index"))

    session["logged_in"] = False
    return render_template("create.html", current_time=time.time())

@app.route("/logout")
def logout():
    sid = session.get("sid")
    session.clear()
    if sid:
        active_sessions.pop(sid, None)
    return redirect(url_for("index"))

# --- background processes
def active_session_cleanup():
    while True:
        now = datetime.now()
        inactive_sids = [
            sid for sid, data in active_sessions.items()
            if (now - datetime.strptime(data['login_time'], '%d/%m %H:%M:%S')).total_seconds() > 3600  # 1 hour
        ]
        for sid in inactive_sids:
            active_sessions.pop(sid, None)

        time.sleep(120) 

'''
cleanup_thread = threading.Thread(target=active_session_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()
'''
