import os
import google.generativeai as genai
import sqlparse
import re
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import database
from database import list_databases, list_tables, list_columns

# Load environment variables
load_dotenv()

# Configure Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Limits to avoid token limit issues
MAX_TABLES = 15
MAX_COLUMNS_PER_TABLE = 10

def clean_sql_output(response_text):
    """Extracts SQL query from AI response and formats it."""
    clean_query = re.sub(r"```sql\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL)
    sql_match = re.search(r"SELECT .*?;", clean_query, re.DOTALL | re.IGNORECASE)
    raw_sql = sql_match.group(0) if sql_match else clean_query.strip()
    return sqlparse.format(raw_sql, reindent=True, keyword_case='upper')

def get_limited_schema():
    """Fetches a reduced database schema to fit within token limits."""
    schema = {}
    databases = list_databases().get("databases", [])
    for db in databases:
        schema[db] = {}
        tables = list_tables(db).get("tables", [])[:MAX_TABLES]
        for table in tables:
            schema[db][table] = list_columns(db, table).get("columns", [])[:MAX_COLUMNS_PER_TABLE]
            
    return schema

def generate_sql_query(nl_query):
    """Converts a natural language query into an optimized SQL query using Gemini."""
    schema = get_limited_schema()
    schema_text = "\n".join([
        f"{table}: {', '.join(columns)}" for db, tables in schema.items() for table, columns in tables.items()
    ])
    
    prompt = f"""
You are an SQL expert. Convert the following natural language query into an optimized SQLite query.
- Do NOT use MySQL-specific syntax.
- Use indexing where applicable.
- Prefer JOINS over subqueries.
- Use GROUP BY for aggregations if needed.
- Return ONLY the raw SQL query. Do not explain the query.

Database Schema (Limited View):
{schema_text}

User Query: {nl_query}

SQL Query:
"""

    try:
        # Use gemini-3.5-flash as the default model
        model = genai.GenerativeModel("gemini-3.5-flash")
        response = model.generate_content(prompt)
        raw_sql_query = response.text.strip()
        return clean_sql_output(raw_sql_query)
        
    except Exception as e:
        return f"Error generating SQL query: {e}"

def execute_query(sql_query):
    try:
        # Code-level validation to block destructive non-SELECT queries
        formatted_query = sqlparse.format(sql_query, strip_comments=True).strip().upper()
        if not (formatted_query.startswith("SELECT") or formatted_query.startswith("WITH") or formatted_query.startswith("PRAGMA")):
            return {"error": "Security Block: Only read-only queries (SELECT) are allowed."}

        with database.engine.connect() as connection:
            result = connection.execute(text(sql_query))
            rows = result.fetchall()

            # Get column names
            column_names = result.keys()

            # Convert results into a list of dictionaries
            formatted_results = [dict(zip(column_names, row)) for row in rows]

            return {"results": formatted_results}

    except SQLAlchemyError as e:
        return {"error": str(e)}
