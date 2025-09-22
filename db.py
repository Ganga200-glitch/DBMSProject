import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="projectuser",
        password="Ganga@2005",
        database="drms"
    )
    return conn
