import streamlit as st
import pandas as pd
from db_connector import create_connection, execute_query, get_table_schema, get_all_table_names
from gemini_handler import get_sql_from_gemini, identify_table_from_prompt, classify_command_type

st.set_page_config(page_title="Cognita", page_icon="🧠", layout="wide")
st.title("Cognita 🧠")
st.write("Query Made Human.")


st.sidebar.header("Database Connection")
db_name = st.sidebar.text_input("Database Name", placeholder="Enter name of the DB")

st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown('[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)](https://github.com/abhnva/Cognita)', unsafe_allow_html=True)

st.info(f"Targeting database: **`{db_name or 'Not Specified'}`**. Your command will be classified before execution.")
user_question = st.text_area("Enter your command/question here:", height=150, placeholder="e.g. Show all students with marks above 90 OR create a new table...")

if st.button("🚀 Execute Command"):
    if not user_question:
        st.warning("Please enter a command or question.")
    else:
        with st.spinner("Classifying your command..."):
            command_type = classify_command_type(user_question)

        conn = None
        if command_type in ["DDL_DATABASE", "SERVER_LEVEL_QUERY"]:
            conn = create_connection()
        elif command_type in ["DDL_CREATE_TABLE", "DDL_ALTER_TABLE", "DDL_DROP_TABLE", "DML", "DQL_SHOW", "DQL"]:
            if db_name:
                conn = create_connection(db_name)
            else:
                st.warning("Please provide a database name in the sidebar for this command.")
        else:
            st.error("Could not classify the command type. Please try rephrasing.")

        if conn:
            if command_type in ["DDL_DATABASE", "SERVER_LEVEL_QUERY"]:
                st.subheader("Server-Level Command Detected")
                with st.spinner("Generating SQL query..."):
                    sql_query = get_sql_from_gemini(user_question, "No schema needed.")
                if sql_query:
                    st.info("Generated SQL Query:"); st.code(sql_query, language='sql')
                    results = execute_query(conn, sql_query)
                    if results is not None:
                        if isinstance(results, list):
                            st.success("Command executed. Results:")
                            st.dataframe(pd.DataFrame(results))
                        else:
                            st.success(f"Command executed successfully!")
                    else: st.error("Error executing server-level command.")
                else: st.error("Failed to generate SQL query.")

            elif command_type == "DQL_SHOW":
                st.subheader("Show Command Detected")
                with st.spinner("Generating SHOW query..."):
                    sql_query = get_sql_from_gemini(user_question, f"Currently in database '{db_name}'.")
                if sql_query:
                    st.info("Generated SQL Query:"); st.code(sql_query, language='sql')
                    results = execute_query(conn, sql_query)
                    if results is not None and isinstance(results, list):
                        st.success("Command executed. Results:")
                        st.dataframe(pd.DataFrame(results))
                    elif results is not None:
                         st.success("Command executed successfully!")
                    else: st.error("Error executing SHOW command.")
                else: st.error("Failed to generate SQL query.")

            elif command_type == "DDL_CREATE_TABLE":
                st.subheader("Create Table Command Detected")
                with st.spinner("Generating CREATE TABLE query..."):
                    schema_context = f"Currently in database '{db_name}'. No existing tables needed for context."
                    sql_query = get_sql_from_gemini(user_question, schema_context)
                if sql_query:
                    st.info("Generated SQL Query:"); st.code(sql_query, language='sql')
                    results = execute_query(conn, sql_query)
                    if results is not None: st.success("Table created successfully!")
                    else: st.error("Error creating table.")
                else: st.error("Failed to generate SQL query.")
            
            elif command_type in ["DDL_ALTER_TABLE", "DDL_DROP_TABLE", "DML", "DQL"]:
                st.subheader(f"Table-Level Command Detected ({command_type})")
                with st.spinner("Discovering tables and identifying context..."):
                    available_tables = get_all_table_names(conn)
                    if not available_tables:
                        st.error("Could not find any tables in this database."); st.stop()
                    
                    table_name = identify_table_from_prompt(user_question, available_tables)
                    if not table_name:
                        st.error("Could not identify a relevant table in your prompt."); st.stop()
                    
                    st.success(f"Identified table: **`{table_name}`**")
                    schema = get_table_schema(conn, table_name)
                    if not schema:
                        st.error(f"Could not fetch schema for table '{table_name}'."); st.stop()
                
                with st.spinner("Generating final SQL query..."):
                    sql_query = get_sql_from_gemini(user_question, schema)
                
                if not sql_query or "INCOMPLETE" in sql_query.upper():
                    st.warning("Request incomplete. For INSERT/UPDATE, please provide all necessary data.")
                else:
                    st.info("Generated SQL Query:"); st.code(sql_query, language='sql')
                    results = execute_query(conn, sql_query)
                    if results is not None:
                        if isinstance(results, list):
                            if results: 
                                st.dataframe(pd.DataFrame(results))
                            else: st.info("Query ran successfully but returned no data.")
                        elif isinstance(results, int):
                            st.success(f"Command executed successfully. {results} row(s) affected.")
                    else:
                        st.error("An error occurred while executing the query.")
            
            conn.close()