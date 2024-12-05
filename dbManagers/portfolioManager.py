import sqlite3 
import json

# two tables, team_portfolios and user_portfolios, with the following schema:
'''
CREATE TABLE sqlite_sequence(name,seq);
sqlite> CREATE TABLE team_portfolios (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PortfolioName VARCHAR NOT NULL,
    UserName VARCHAR NOT NULL,
    UserTeam VARCHAR NOT NULL,
    PortfolioData JSON NOT NULL
);
'''

def fetchAllTeamPortfolios(user_team: str):
    try:
        with sqlite3.connect('databases/portfolios.db') as conn:
            cursor = conn.cursor()

            if user_team=="": return False

            elif user_team=="other":
                cursor.execute('SELECT PortfolioName, UserName, UserTeam, PortfolioData FROM team_portfolios')
            else:
                cursor.execute('SELECT PortfolioName, UserName, UserTeam, PortfolioData FROM team_portfolios WHERE UserTeam =?',(user_team,))
                    
            rows = cursor.fetchall()

            data = []

            for i in rows:
                portfolio_name = i[0]
                user_name = [1]
                user_team = i[2]
                portfolio_data = i[3]
                portfolio_data_list = json.loads(portfolio_data)
                package = [portfolio_name,user_name,user_team,portfolio_data_list]
                data.append(package)

    except sqlite3.OperationalError as e:
        return e

    return data

def fetchAllUserPortfolios(user_name: str):
    try:
        with sqlite3.connect('databases/portfolios.db') as conn:
            cursor = conn.cursor()

            if user_name=="": return False
            elif user_name=="admin":
                cursor.execute('SELECT PortfolioName, UserName, UserTeam, PortfolioData FROM user_portfolios')
            else:
                cursor.execute('SELECT PortfolioName, UserName, UserTeam, PortfolioData FROM user_portfolios WHERE UserName =?',(user_name,))
                    
            rows = cursor.fetchall()

            data = []

            for i in rows:
                portfolio_name = i[0]
                user_name = [1]
                user_team = i[2]
                portfolio_data = i[3]
                portfolio_data_list = json.loads(portfolio_data)
                package = [portfolio_name,user_name,user_team,portfolio_data_list]
                data.append(package)

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return data

def fetchPortfolio(portfolio_name:str="", user_name: str="",user_team:str = ""):
    try:
        with sqlite3.connect('databases/portfolios.db') as conn:
            cursor = conn.cursor()

            if user_name=="" and user_team=="": return False
            elif user_name!="" and user_team!="": return False

            elif user_name!="":
                cursor.execute('SELECT PortfolioName, UserName, UserTeam, PortfolioData FROM user_portfolios WHERE PortfolioName = ? AND UserName =?',(portfolio_name,user_name))
            elif user_team!="":
                cursor.execute('SELECT PortfolioName, UserName, UserTeam, PortfolioData FROM team_portfolios WHERE PortfolioName = ? AND UserTeam =?',(portfolio_name,user_team))
            
            else: return False

            rows = cursor.fetchall()

            data = []

            for i in rows:
                portfolio_name = i[0]
                user_name = [1]
                user_team = i[2]
                portfolio_data = i[3]
                portfolio_data_list = json.loads(portfolio_data)
                package = [portfolio_name,user_name,user_team,portfolio_data_list]
                data.append(package)

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return data


def insertPortfolio(portfolio_name:str ,user_name:str, user_team: str, portfolio_classification:str , portfolioData: list):
    portfolioDataJSON = json.dumps(portfolioData)

    try:
        with sqlite3.connect('databases/portfolios.db') as conn:
            cursor = conn.cursor()
            if portfolio_classification=="user":
                cursor.execute('INSERT INTO user_portfolios (PortfolioName, UserName, UserTeam, PortfolioData) VALUES (?, ?, ?, ?)',(portfolio_name, user_name, user_team,portfolioDataJSON))
            elif portfolio_classification=="team":
                cursor.execute('INSERT INTO team_portfolios (PortfolioName, UserName, UserTeam, PortfolioData) VALUES (?, ?, ?, ?)',(portfolio_name, user_name, user_team,portfolioDataJSON))
            else: return False
            conn.commit()

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return True

def deletePortfolio(class_name: str):
    try:
        with sqlite3.connect('databases/portfolios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM portfolios WHERE ClassName =?',(class_name,))
            row = cursor.fetchall()
            conn.commit()

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return row

def modifyPortfolio(class_name:str, modified_portfolio:list):
    modified_portfolio = json.dumps(modified_portfolio)

    try:
        with sqlite3.connect('databases/portfolios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE portfolios SET PortfolioData=? WHERE ClassName =?',(modified_portfolio,class_name))
            conn.commit()

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return True