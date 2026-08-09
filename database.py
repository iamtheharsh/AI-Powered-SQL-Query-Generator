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

# Create SQLAlchemy engine
try:
    logging.debug(f"Connecting to SQLite database at {SQLITE_DB_PATH}")
    engine = create_engine(DATABASE_URL, echo=True)
    logging.debug("Database connection successful!")
except Exception as e:
    logging.error(f"Database connection failed: {str(e)}")
    exit()


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
            # PRAGMA table_info returns (cid, name, type, notnull, dflt_value, pk)
            # The column name is at index 1 (row[1])
            result = connection.execute(
                text(f"PRAGMA table_info('{table_name}');")
            ).fetchall()
            return {"columns": [row[1] for row in result]}
    except Exception as e:
        return {"error": str(e)}