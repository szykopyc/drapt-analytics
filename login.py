import bcrypt
import sqlite3
import random
from tqdm import tqdm 

def checkCredentials(username, password, team):
    try:
        with sqlite3.connect('details.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Username, Password, Team, PermissionScope FROM loginCreds WHERE Username =?', (username,))
            row = cursor.fetchone()

            if row is None:
                return [False,0]

    except sqlite3.OperationalError as e:
        return [False, 0]
    
    stored_hashed_password = row[1]
    stored_team = row[2]
    stored_scope = row[3]

    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password) and stored_team == team:
        return [True,stored_scope]
    else:
        return [False,0]

def fetchAllCreds():
    try:
        with sqlite3.connect('details.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Username, FullName, Team, PermissionScope, PhoneNumber  FROM loginCreds')
            row = cursor.fetchall()

            if row is None:
                return False

    except sqlite3.OperationalError as e:
        print(e)
        return False
    
    return row

def create_table():
    conn = sqlite3.connect("details.db")
    cursor = conn.cursor()
    query = "DROP TABLE IF EXISTS loginCreds"
    cursor.execute(query)
    conn.commit()
    
    query = "CREATE TABLE loginCreds(Username VARCHAR UNIQUE, FullName VARCHAR, Password VARCHAR, Team VARCHAR, PhoneNumber VARCHAR, PermissionScope VARCHAR)"
    cursor.execute(query)
    conn.commit()

def enter(username, fname ,password, team, phoneNumber, permissionScope):
    if username and password and team and phoneNumber and permissionScope:
        conn = sqlite3.connect("details.db")
        cursor = conn.cursor()

        # Ensure password is hashed using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Using parameterized query to prevent SQL injection
        query = "INSERT INTO loginCreds (Username, FullName, Password, Team, PhoneNumber, PermissionScope) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(query, (username, fname, hashed_password, team, phoneNumber, permissionScope))
        conn.commit()

    else:
        return False

def deleteUser(username):
    try:
        with sqlite3.connect('details.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM loginCreds WHERE Username = ?',(username,))
            conn.commit()
            return True
    except Exception as e:
        print(e)
        return False


if __name__=="__main__":
    categories = ['industrials','tmt','usc']
    for i in tqdm(range(30)):
        enter(f"user{str(i)}","abc",f"{random.choice(categories)}",f"+447{random.randint(111111111,999999999)}",f"{random.randint(1,3)}")
