import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.title("🤖 AI-Powered SQL Query Generator & Executor")
st.markdown("This app allows you to generate and execute SQL queries using AI.")

# Fetch available databases
st.sidebar.header("Database Selection")
if st.sidebar.button("🔍 List Databases"):
    response = requests.get(f"{API_URL}/list_databases/")
    if response.status_code == 200:
        databases = response.json().get("databases", [])
        st.sidebar.write("### Available Databases:")
        st.sidebar.write(databases)
    else:
        st.sidebar.error("Error fetching databases")

# Select a database
selected_db = st.sidebar.text_input("Enter Database Name:")
if selected_db:
    # Fetch tables
    if st.sidebar.button("📂 Show Tables"):
        response = requests.get(f"{API_URL}/list_tables/{selected_db}")
        if response.status_code == 200:
            tables = response.json().get("tables", [])
            st.sidebar.write("### Tables in Database:")
            st.sidebar.write(tables)
        else:
            st.sidebar.error("Error fetching tables")

# Select a table
selected_table = st.sidebar.text_input("Enter Table Name:")
if selected_db and selected_table:
    # Fetch columns
    if st.sidebar.button("📋 Show Columns"):
        response = requests.get(f"{API_URL}/list_columns/{selected_db}/{selected_table}")
        if response.status_code == 200:
            columns = response.json().get("columns", [])
            st.sidebar.write("### Columns in Table:")
            st.sidebar.write(columns)
        else:
            st.sidebar.error("Error fetching columns")

# Main content area
if not selected_db:
    st.info("👈 Please enter a Database Name in the sidebar to start generating and executing queries.")
else:
    st.header("🧠 AI-Powered SQL Generation")
    natural_language_query = st.text_area("Enter your query in plain English:")
    if st.button("⚡ Generate SQL"):
        response = requests.post(f"{API_URL}/generate_sql/", params={"natural_language_query": natural_language_query})
        if response.status_code == 200:
            generated_sql = response.json().get("sql_query", "")
            st.code(generated_sql, language='sql')
        else:
            st.error("Error generating SQL query")
            
    st.header("🖥️ Execute SQL Query")
    manual_sql_query = st.text_area("Enter SQL query to execute:")
    if st.button("🚀 Run Query"):
        response = requests.post(f"{API_URL}/execute_sql/", params={"sql_query": manual_sql_query})
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                st.write("### Query Results:")
                st.table(results)
            else:
                st.write("No results found.")
        else:
            st.error("Error executing query")
