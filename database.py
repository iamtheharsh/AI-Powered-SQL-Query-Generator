import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# SQLite database file path
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "chinook.db")

# Connection String
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Global engine variable
engine = None

def set_database_file(db_path: str):
    global engine, DATABASE_URL
    DATABASE_URL = f"sqlite:///{db_path}"
    try:
        logging.debug(f"Connecting to SQLite database at {db_path}")
        engine = create_engine(DATABASE_URL, echo=True)
        logging.debug("Database connection successful!")
        return True
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        return False

# Initialize the default engine
set_database_file(SQLITE_DB_PATH)


# Function to list databases (SQLite has one main database)
def list_databases():
    try:
        return {"databases": ["main"]}
    except Exception as e:
        return {"error": str(e)}


# Function to list tables
def list_tables(database_name="main"):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            ).fetchall()
            return {"tables": [row[0] for row in result]}
    except Exception as e:
        return {"error": str(e)}


# Function to list columns
def list_columns(database_name, table_name):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(f"PRAGMA table_info('{table_name}');")
            ).fetchall()
            return {"columns": [row[1] for row in result]}
    except Exception as e:
        return {"error": str(e)}