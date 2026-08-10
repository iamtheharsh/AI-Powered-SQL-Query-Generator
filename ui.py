import streamlit as st
import requests
import pandas as pd

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

st.title("🤖 AI-Powered SQL Query Generator & Executor")
st.markdown("This app allows you to generate and execute SQL queries using AI.")

# Initialize session state variables
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""
if "query_results" not in st.session_state:
    st.session_state.query_results = None
if "explanation" not in st.session_state:
    st.session_state.explanation = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "uploaded_db_name" not in st.session_state:
    st.session_state.uploaded_db_name = ""
if "manual_sql_query" not in st.session_state:
    st.session_state.manual_sql_query = ""

# Sidebar Database Selection
st.sidebar.header("Database Selection")

# File uploader for custom database
uploaded_file = st.sidebar.file_uploader("Upload SQLite Database (.db, .sqlite)", type=["db", "sqlite"])
if uploaded_file is not None:
    # If a new file is uploaded
    if st.session_state.uploaded_db_name != uploaded_file.name:
        # Send the file to the backend
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
        upload_response = requests.post(f"{API_URL}/upload_db/", files=files)
        if upload_response.status_code == 200:
            st.session_state.uploaded_db_name = uploaded_file.name
            st.sidebar.success(f"Connected to: {uploaded_file.name}")
            # Reset query results, generated SQL, and explanation for the new database
            st.session_state.generated_sql = ""
            st.session_state.query_results = None
            st.session_state.explanation = ""
            st.rerun()
        else:
            st.sidebar.error("Error uploading database to backend")

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
    index=1 if len(databases) > 0 else 0  # Default to 'main' if loaded
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

# Helper function to add query to history
def add_to_history(query):
    query = query.strip()
    if query and query not in st.session_state.history:
        st.session_state.history.append(query)
        if len(st.session_state.history) > 5:
            st.session_state.history.pop(0)

# Sidebar Query History
st.sidebar.header("📜 Query History Log")
if st.session_state.history:
    for idx, hist_query in enumerate(reversed(st.session_state.history)):
        short_query = hist_query.replace("\n", " ")[:30] + "..." if len(hist_query) > 30 else hist_query.replace("\n", " ")
        if st.sidebar.button(f"{short_query}", key=f"hist_{idx}"):
            st.session_state.manual_sql_query = hist_query
            st.rerun()
else:
    st.sidebar.write("No queries run yet.")

# Reusable function to display table, download button, and visual charts
def display_results(results, title="Query Results"):
    if not results:
        st.write("No results found.")
        return

    df = pd.DataFrame(results)
    st.write(f"### {title}:")
    st.dataframe(df)

    # Download Button
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download results as CSV",
        data=csv_data,
        file_name="query_results.csv",
        mime="text/csv",
        key=f"dl_{title}"
    )


# Main content area
if not selected_db:
    st.info("👈 Please select or upload a Database in the sidebar to start generating and executing queries.")
else:
    st.header("🧠 AI-Powered SQL Generation")
    natural_language_query = st.text_area("Enter your query in plain English:")
    if st.button("⚡ Generate SQL"):
        # Reset previous generated SQL, results, and explanation
        st.session_state.generated_sql = ""
        st.session_state.query_results = None
        st.session_state.explanation = ""
        
        response = requests.post(f"{API_URL}/generate_sql/", params={"natural_language_query": natural_language_query})
        if response.status_code == 200:
            st.session_state.generated_sql = response.json().get("sql_query", "")
        else:
            st.error("Error generating SQL query")
            
    # Display generated SQL and execution/explanation buttons
    if st.session_state.generated_sql:
        st.code(st.session_state.generated_sql, language='sql')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Run Generated Query"):
                run_response = requests.post(f"{API_URL}/execute_sql/", params={"sql_query": st.session_state.generated_sql})
                if run_response.status_code == 200:
                    st.session_state.query_results = run_response.json().get("results", [])
                    add_to_history(st.session_state.generated_sql)
                    st.rerun()
                else:
                    st.error("Error executing query")
        with col2:
            if st.button("💡 Explain Query"):
                explain_response = requests.post(f"{API_URL}/explain_sql/", params={"sql_query": st.session_state.generated_sql})
                if explain_response.status_code == 200:
                    st.session_state.explanation = explain_response.json().get("explanation", "")
                else:
                    st.error("Error explaining SQL query")

    # Display explanation if loaded
    if st.session_state.explanation:
        st.info(f"### 💡 AI Explanation:\n{st.session_state.explanation}")
                
    # Display query execution results
    if st.session_state.query_results is not None:
        display_results(st.session_state.query_results, title="AI Query Results")
            
    st.header("🖥️ Execute SQL Query Manually")
    manual_sql_query = st.text_area("Enter custom SQL query to execute:", value=st.session_state.manual_sql_query)
    if st.button("🚀 Run Custom Query"):
        manual_response = requests.post(f"{API_URL}/execute_sql/", params={"sql_query": manual_sql_query})
        if manual_response.status_code == 200:
            manual_results = manual_response.json().get("results", [])
            add_to_history(manual_sql_query)
            display_results(manual_results, title="Custom Query Results")
        else:
            st.error("Error executing custom query")
