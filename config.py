import os
from dotenv import load_dotenv

load_dotenv()

DB_DRIVER = "ODBC Driver 17 for SQL Server"

OLTP_SERVER = os.getenv("OLTP_SERVER")
OLTP_DATABASE = os.getenv("OLTP_DATABASE")
OLTP_USER = os.getenv("OLTP_USER")
OLTP_PASSWORD = os.getenv("OLTP_PASSWORD")

OLTP_CONN_STRING = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={OLTP_SERVER};"
    f"DATABASE={OLTP_DATABASE};"
    f"UID={OLTP_USER};"
    f"PWD={OLTP_PASSWORD};"
)

OLAP_SERVER = os.getenv("OLAP_SERVER")
OLAP_DATABASE = os.getenv("OLAP_DATABASE")
OLAP_USER = os.getenv("OLAP_USER")
OLAP_PASSWORD = os.getenv("OLAP_PASSWORD")

OLAP_CONN_STRING = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={OLAP_SERVER};"
    f"DATABASE={OLAP_DATABASE};"
    f"UID={OLAP_USER};"
    f"PWD={OLAP_PASSWORD};"
)
