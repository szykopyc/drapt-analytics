#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 17:27:47 2024

@author: szymonkopycinski
"""
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify # type: ignore
from random import choice, randint
from dbManagers.loginManager import checkCredentials, enter, fetchAllCreds, deleteUser
import dbManagers.portfolioManager as portfolio_manager
import os
from datetime import timedelta, datetime
import time
import threading
import uuid
import risks.portfolio
import json
import numpy as np
import pandas as pd
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True # delete this in production


app.secret_key = os.environ.get('SECRET_KEY')

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

enable_nefs_logo = False

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
                "user_name": username,
                "user_team": userGroup,
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
    return render_template("index.html", verification_list=verification_list, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)


@app.route("/home")
def home():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)
        
        else:
            return render_template("home.html",admin=False, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)
    
    else:
        session.clear()
        return redirect(url_for("index"))

@app.route("/risk", methods=["GET", "POST"])
def risk():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        user_data = active_sessions[session["sid"]]
        user_name = user_data["user_name"]
        user_team = user_data["user_team"]
        manager_status = int(user_data["permission_scope"]) # this is so that managers have the option whether to create a custom portfolio or team portfolio

        if manager_status>1: manager_status = True
        else: manager_status = False

        monteCarloData = None
        createCustomPortfolioPage = False
        portfolio_name=None
        portfolio_tickers_and_weights=None
        risk_metric_data = None
        performanceData= None
        histogramData = None
        correlationMatrix = None
        correlationMatrixMostCorrelated = None
        correlationMatrixLeastCorrelated = None
        portfolio_rolling_vol = None

        totalReturnMetric = None

        noPortfolioError = False

        lookback_period=None

        risk_free_rates = {
            1: 0.0450,
            2: 0.0425,
            3: 0.0400,
            4: 0.0375,
            5: 0.0355
        }

        risk_free_rate = 0

        jensenAlpha = None

        if request.method == "POST":
            portfolio_name = request.form.get("portfolio_name")

            lookback_days = 365 * float(request.form.get("historical-data-range"))
            lookback_days = round(lookback_days, 0)

            # Convert to years without rounding
            lookback_years = lookback_days / 365  

            # Determine lookback period display format
            if lookback_years >= 1:
                lookback_period = f"{lookback_years:.2f} years"
                if lookback_years == 1:
                    lookback_period = "1 year"
            else:
                # Handle cases where lookback period is less than 1 year
                lookback_period = f"{int(lookback_days)} days"

            # Find the largest available risk-free period that does not exceed lookback_years
            if lookback_years >= 1:
                available_periods = sorted(risk_free_rates.keys())  # [1, 2, 3, 4, 5]
                chosen_period = max(p for p in available_periods if p <= lookback_years)
            else:
                # If the lookback period is less than 1 year, pick the appropriate period based on available data
                chosen_period = min(risk_free_rates.keys())  # Choose the smallest available period

            # Assign correct risk-free rate
            risk_free_rate = risk_free_rates[chosen_period]

            enable_monte_carlo_sim = request.form.get("enable-monte-carlo")
            if enable_monte_carlo_sim =="enable-monte-carlo":
                enable_monte_carlo_sim = True
            else:
                enable_monte_carlo_sim = False

            if portfolio_name == "custom_portfolio":
                createCustomPortfolioPage = True
            
            elif portfolio_name==None or portfolio_name=="":
                noPortfolioError=True

            else:
                createCustomPortfolioPage = False

                if portfolio_name[:5] == "user_":
                    portfolio_name = portfolio_name[5:]
                    selected_portfolio_data = portfolio_manager.fetchPortfolio(portfolio_name=portfolio_name, user_name=user_name)

                elif portfolio_name[:5] == "team_":
                    portfolio_name = portfolio_name[5:]
                    selected_portfolio_data = portfolio_manager.fetchPortfolio(portfolio_name=portfolio_name, user_team=user_team)
                
                portfolio_tickers_and_weights = selected_portfolio_data[0][3]

                portfolio = risks.portfolio.Portfolio(portfolio_tickers_and_weights,lookback_days,risk_free_rate)

                portfolio_volatility_daily = portfolio.compute_volatility()
                portfolio_volatility_weekly = portfolio.compute_volatility() * np.sqrt(5)
                portfolio_volatility_monthly = portfolio.compute_volatility() * np.sqrt(20)
                portfolio_variance = portfolio.compute_variance()
                portfolio_sharpe = portfolio.compute_sharpe()
                portfolio_sortino = portfolio.compute_sortino()
                portfolio_var95 = portfolio.calculate_var(0.95)
                portfolio_var99 = portfolio.calculate_var(0.99)
                portfolio_beta = portfolio.beta
                portfolio_skewness = portfolio.skewness

                jensenAlpha=portfolio.jensens_alpha

                portfolio_rolling_vol = portfolio.gen_rolling_volatility().to_json(orient='split')
                # Convert the dictionary to JSON
                # portfolio_rolling_vol = portfolio_rolling_vol.to_json(orient="split")

                risk_metric_data = [portfolio_volatility_daily,portfolio_volatility_weekly,portfolio_volatility_monthly, jensenAlpha,portfolio_beta, portfolio_sharpe, portfolio_var95, portfolio_var99, portfolio_skewness, portfolio_sortino]

                if enable_monte_carlo_sim:
                    monteCarloSimulation = portfolio.simulate_monte_carlo(num_simulations=10000, lookahead_days=120, initial_value=100)
                    
                    monteCarloData = monteCarloSimulation.to_json(orient="split")
                else:
                    monteCarloData = None

                performanceData = portfolio.portfolio_data_cumsum.to_json(orient="split")
                histogramData = portfolio.portfolio_data.to_json(orient="split")
                correlationMatrixData = portfolio.compute_correlation_matrix()
                correlationMatrix = correlationMatrixData[0].to_json()
                correlationMatrixMostCorrelated = correlationMatrixData[1]
                correlationMatrixLeastCorrelated = correlationMatrixData[2]

                totalReturnMetric = portfolio.portfolio_data_cumsum['Portfolio'].iloc[-1]

                def format_correlation_data(df, limit_to_top=3):
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        # Sort each pair of 'Asset 1' and 'Asset 2'
                        sorted_assets = df[['Asset 1', 'Asset 2']].apply(lambda row: sorted([row['Asset 1'], row['Asset 2']]), axis=1)
                        
                        # Assign the sorted values back to the dataframe
                        df[['Asset 1', 'Asset 2']] = pd.DataFrame(sorted_assets.tolist(), index=df.index)

                        # Filter out duplicate pairs (e.g., both CSGOLD.SW-JPM and JPM-CSGOLD.SW)
                        df_unique = df.drop_duplicates(subset=['Asset 1', 'Asset 2'])

                        # Round the correlation values to 2 decimal places
                        df_unique['Correlation'] = df_unique['Correlation'].round(2)

                        # Take only the top 'limit_to_top' rows based on the magnitude of the correlation (both positive and negative)
                        top_correlations = df_unique.nlargest(limit_to_top, 'Correlation', 'all')

                        # Convert the DataFrame to a list of lists (2D array)
                        correlation_array = top_correlations[['Asset 1', 'Asset 2', 'Correlation']].values.tolist()

                        return correlation_array
                    else:
                        return []

                correlationMatrixMostCorrelated=format_correlation_data(correlationMatrixMostCorrelated)
                correlationMatrixLeastCorrelated=format_correlation_data(correlationMatrixLeastCorrelated)


        try:
            available_portfolios_for_team = portfolio_manager.fetchAllTeamPortfolios(user_team=user_team)
            available_portfolios_for_user = portfolio_manager.fetchAllUserPortfolios(user_name=user_name)
            available_team_portfolios = []
            available_user_portfolios = []
            for i in available_portfolios_for_team:
                available_team_portfolios.append(i)

            for i in available_portfolios_for_user:
                available_user_portfolios.append(i)

        except Exception as e:
            print("EXCEPTION OCCURRED *********************")
            print(e)
            portfolio_tickers_and_weights = [[]]
        
        # fetched portfolio data comes in the format (teamname, [[TICKER, WEIGHT],[TICKER,WEIGHT]])

        if session.get("adminLoggedIn") ==True:
            return render_template("risk.html",admin=True, manager_status=manager_status,current_time=time.time(),noPortfolioError=noPortfolioError,portfolio_name=portfolio_name,portfolio_tickers_and_weights=portfolio_tickers_and_weights,monteCarloData=monteCarloData, correlationMatrixData=correlationMatrix, correlationMatrixMostCorrelated=correlationMatrixMostCorrelated, correlationMatrixLeastCorrelated=correlationMatrixLeastCorrelated,risk_metric_data = risk_metric_data,performanceData=performanceData,histogramData=histogramData,available_team_portfolios=available_team_portfolios,available_user_portfolios= available_user_portfolios,createCustomPortfolioPage=createCustomPortfolioPage, lookback_period=lookback_period, totalReturnMetric=totalReturnMetric,enable_nefs_logo=enable_nefs_logo,portfolio_rolling_vol=portfolio_rolling_vol)
        
        else:
            return render_template("risk.html",admin=False, manager_status=manager_status,current_time=time.time(), noPortfolioError=noPortfolioError,portfolio_name=portfolio_name,portfolio_tickers_and_weights=portfolio_tickers_and_weights,monteCarloData=monteCarloData, correlationMatrixData=correlationMatrix,correlationMatrixMostCorrelated=correlationMatrixMostCorrelated, correlationMatrixLeastCorrelated=correlationMatrixLeastCorrelated,risk_metric_data = risk_metric_data,performanceData=performanceData,histogramData=histogramData,available_team_portfolios=available_team_portfolios,available_user_portfolios= available_user_portfolios,createCustomPortfolioPage=createCustomPortfolioPage, lookback_period=lookback_period, totalReturnMetric=totalReturnMetric,enable_nefs_logo=enable_nefs_logo,portfolio_rolling_vol=portfolio_rolling_vol)
    
    else:
        session.clear()
        return redirect(url_for("index"))

@app.route("/performance")
def performance():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)
        
        else:
            return render_template("home.html",admin=False, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)
    
    else:
        session.clear()
        return redirect(url_for("index"))

@app.route("/profile")
def profile():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            return render_template("home.html",admin=True, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)
        
        else:
            return render_template("home.html",admin=False, current_time=time.time(),enable_nefs_logo=enable_nefs_logo)
    
    else:
        session.clear()
        return redirect(url_for("index"))




@app.route("/admin")
def admin_panel():
    if session.get("logged_in")==True and session.get("sid") in active_sessions:
        if session.get("adminLoggedIn") ==True:
            userCreds = fetchAllCreds()
            userScope = session.get("userPermissionScope")

            return render_template("admin_panel.html", userScope=userScope,active_sessions=active_sessions, session=session, userCreds=userCreds, current_time=time.time(), admin=True,enable_nefs_logo=enable_nefs_logo)
        
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

        flash(f"{user_data['user_name']}")

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


@app.route("/create-portfolio", methods=["GET","POST"])
def create_portfolio():
    # Ensure the user is logged in and has a valid session ID
    if not session.get("logged_in") == True and session.get("sid") not in active_sessions:
        return redirect(url_for("index"))

    # Get the portfolio data from the request
    data = request.json  # Ensure that the request sends valid JSON data
    if not data or 'portfolio' not in data:
        return jsonify({"status": "error", "message": "Portfolio data missing"}), 400

    portfolio_name = data['portfolioName'] 
    portfolio = [[item['ticker'], item['weight']] for item in data['portfolio']]
    try:
        portfolio_classification = data['portfolioFor']
    except:
        portfolio_classification = "user"


    # Validate the portfolio
    if len(portfolio) >= 2 and sum([row[1] for row in portfolio]) == 1.0:
        # Portfolio is valid

        session['createCustomPortfolioPage'] = False
        user_data = active_sessions[session["sid"]]
        user_name = user_data["user_name"]
        user_team = user_data["user_team"]
        
        portfolio_manager.insertPortfolio(portfolio_name, user_name,user_team, portfolio_classification, portfolio)
        return jsonify({"status": "success", "redirect_url": "/risk"}), 200
    else:
        # Handle invalid portfolio case
        return jsonify({"status": "error", "message": "Invalid portfolio data"}), 400

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