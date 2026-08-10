import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.title("🤖 AI-Powered SQL Query Generator & Executor")
st.markdown("This app allows you to generate and execute SQL queries using AI.")

# Initialize session state variables
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""
if "query_results" not in st.session_state:
    st.session_state.query_results = None

# Sidebar Database Selection
st.sidebar.header("Database Selection")

# Automatically fetch databases on load
databases = []
db_response = requests.get(f"{API_URL}/list_databases/")
if db_response.status_code == 200:
    databases = db_response.json().get("databases", [])
else:
    st.sidebar.error("Error fetching databases")

# Selectbox for Database
selected_db = st.sidebar.selectbox(
    "Select Database Name:",
    options=[""] + databases,
    index=0
)

tables = []
selected_table = ""

if selected_db:
    # Automatically fetch tables when DB is selected
    tables_response = requests.get(f"{API_URL}/list_tables/{selected_db}")
    if tables_response.status_code == 200:
        tables = tables_response.json().get("tables", [])
    else:
        st.sidebar.error("Error fetching tables")

    # Selectbox for Table
    selected_table = st.sidebar.selectbox(
        "Select Table Name:",
        options=[""] + tables,
        index=0
    )

if selected_db and selected_table:
    # Automatically fetch columns and show table preview when table is selected
    columns_response = requests.get(f"{API_URL}/list_columns/{selected_db}/{selected_table}")
    if columns_response.status_code == 200:
        columns = columns_response.json().get("columns", [])
        st.sidebar.write("### Columns in Table:")
        st.sidebar.write(columns)
    else:
        st.sidebar.error("Error fetching columns")

    # Fetch table preview (first 5 rows)
    preview_query = f"SELECT * FROM {selected_table} LIMIT 5;"
    preview_response = requests.post(f"{API_URL}/execute_sql/", params={"sql_query": preview_query})
    if preview_response.status_code == 200:
        preview_data = preview_response.json().get("results", [])
        if preview_data:
            st.sidebar.write("### Table Preview (First 5 Rows):")
            st.sidebar.dataframe(preview_data)
        else:
            st.sidebar.write("Table is empty.")
    else:
        st.sidebar.error("Error fetching table preview")

# Main content area
if not selected_db:
    st.info("👈 Please select a Database in the sidebar to start generating and executing queries.")
else:
    st.header("🧠 AI-Powered SQL Generation")
    natural_language_query = st.text_area("Enter your query in plain English:")
    if st.button("⚡ Generate SQL"):
        # Reset previous generated SQL and results
        st.session_state.generated_sql = ""
        st.session_state.query_results = None
        
        response = requests.post(f"{API_URL}/generate_sql/", params={"natural_language_query": natural_language_query})
        if response.status_code == 200:
            st.session_state.generated_sql = response.json().get("sql_query", "")
        else:
            st.error("Error generating SQL query")
            
    # Display generated SQL and one-click run option
    if st.session_state.generated_sql:
        st.code(st.session_state.generated_sql, language='sql')
        if st.button("🚀 Run Generated Query"):
            run_response = requests.post(f"{API_URL}/execute_sql/", params={"sql_query": st.session_state.generated_sql})
            if run_response.status_code == 200:
                st.session_state.query_results = run_response.json().get("results", [])
            else:
                st.error("Error executing query")
                
    # Display query execution results
    if st.session_state.query_results is not None:
        if st.session_state.query_results:
            st.write("### Query Results:")
            st.dataframe(st.session_state.query_results) # Using dataframe for interactive tables
        else:
            st.write("No results found.")
            
    st.header("🖥️ Execute SQL Query Manually")
    manual_sql_query = st.text_area("Enter custom SQL query to execute:")
    if st.button("🚀 Run Custom Query"):
        manual_response = requests.post(f"{API_URL}/execute_sql/", params={"sql_query": manual_sql_query})
        if manual_response.status_code == 200:
            manual_results = manual_response.json().get("results", [])
            if manual_results:
                st.write("### Custom Query Results:")
                st.dataframe(manual_results)
            else:
                st.write("No results found.")
        else:
            st.error("Error executing custom query")
