import os
from urllib.parse import quote_plus

from flask_migrate import Config

def get_database_uri():
    SQL_SERVER = os.getenv("SQL_SERVER", "localhost")
    SQL_DATABASE = "MovieTrackerDB"
    SQL_USER_NAME = os.getenv("SQL_USER_NAME", "")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD", "")

    
    
    connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DATABASE};"
            f"UID={SQL_USER_NAME};"
            f"PWD={SQL_PASSWORD};"
            "TrustServerCertificate=yes;"
            "Encrypt=yes;"
        )

    return ("mssql+pyodbc:///?odbc_connect=" + quote_plus(connection_string))

class Config:
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False