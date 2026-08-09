from fastapi import FastAPI, Query
import logging
from database import list_databases, list_tables, list_columns
from query_generator import generate_sql_query, execute_query

# Initialize FastAPI
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# API: List all databases
@app.get("/list_databases/")
def get_databases():
    return list_databases()

# API: List tables in a database
@app.get("/list_tables/{database_name}")
def get_tables(database_name: str):
    return list_tables(database_name)

# API: List columns in a table
@app.get("/list_columns/{database_name}/{table_name}")
def get_columns(database_name: str, table_name: str):
    return list_columns(database_name, table_name)

# API: Generate SQL query from Natural Language
@app.post("/generate_sql/")
def generate_sql(natural_language_query: str):
    logging.debug(f"Generating SQL for: {natural_language_query}")
    sql_query = generate_sql_query(natural_language_query)
    
    if sql_query:
        return {"sql_query": sql_query}
    return {"error": "Failed to generate SQL"}

# API: Execute SQL query
@app.post("/execute_sql/")
def execute_sql(sql_query: str = Query(..., description="SQL query to execute")):
    """Execute the given SQL query and return results in JSON format."""
    result = execute_query(sql_query)
    return result  # Now properly formatted for FastAPI JSON response
