import sqlite3 
import json

def fetchPortfolio(portfolio_name:str="", user_name: str="",user_group:str = ""):

    try:
        with sqlite3.connect('databases/team_portfolios.db') as conn:
            cursor = conn.cursor()
            if user_name != "" and portfolio_name=="":
                    cursor.execute('SELECT * FROM portfolios WHERE UserName =?',(user_name,))
                    
                    rows = cursor.fetchall()

                    return_2dList = []

                    for i in rows:
                        portfolio_name = i[0]
                        user_name = [1]
                        user_group = i[2]
                        portfolio_data = i[3]
                        portfolio_data_list = json.loads(portfolio_data)
                        package = [portfolio_name,user_name,user_group,portfolio_data_list]
                        return_2dList.append(package)

            elif user_group!= "" and user_name=="":
                if user_group=="other":
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM portfolios')
                else:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM portfolios WHERE UserGroup =?',(user_group,))
                

                rows = cursor.fetchall()
                return_2dList = []

                for i in rows:
                    portfolio_name = i[0]
                    user_name = [1]
                    user_group = i[2]
                    portfolio_data = i[3]
                    portfolio_data_list = json.loads(portfolio_data)
                    package = [portfolio_name,user_name,user_group,portfolio_data_list]
                    return_2dList.append(package)


            else:
                if portfolio_name!="" and user_name!="":
                    cursor.execute('SELECT * FROM portfolios WHERE PortfolioName =? AND UserName =?',(portfolio_name,user_name))

                elif portfolio_name!="" and user_group!="":
                    cursor.execute('SELECT * FROM portfolios WHERE PortfolioName =? AND UserGroup =?',(portfolio_name,user_group))
                
                rows = cursor.fetchall()

                return_2dList = []

                for i in rows:
                    portfolio_name = i[0]
                    user_name = i[1]
                    user_group = i[2]
                    portfolio_data = i[3]
                    portfolio_data_list = json.loads(portfolio_data)
                    package = [portfolio_name,user_name,user_group,portfolio_data_list]
                    return_2dList.append(package)

            conn.commit()        

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return return_2dList


def insertPortfolio(portfolio_name:str ,user_name:str,user_group: str, portfolioData: list):
    portfolioDataJSON = json.dumps(portfolioData)

    try:
        with sqlite3.connect('databases/team_portfolios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO portfolios (PortfolioName, UserName ,UserGroup ,PortfolioData) VALUES (?, ?, ?, ?)',(portfolio_name, user_name, user_group,portfolioDataJSON))
            conn.commit()

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return True

def deletePortfolio(class_name: str):
    try:
        with sqlite3.connect('databases/team_portfolios.db') as conn:
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
        with sqlite3.connect('databases/team_portfolios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE portfolios SET PortfolioData=? WHERE ClassName =?',(modified_portfolio,class_name))
            conn.commit()

    except sqlite3.OperationalError as e:
        print(e)
        return False

    return True