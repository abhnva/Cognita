import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# API key configuration
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring API key: {e}")



def identify_table_from_prompt(user_question, available_tables):
    # Prompt for exact table name matching
    prompt = f"""
    Given a list of available MySQL tables with their exact capitalization: {available_tables}
    
    Analyze the user's prompt and identify which single table from the provided list is the most relevant.
    Your only job is to return that single table name.
    
    CRITICAL: You must respond with the table name exactly as it appears in the list, preserving the original lowercase/uppercase letters.
    
    For example, if the tables are ['SalesData', 'employees'] and the prompt is 'show all staff', you must respond with 'employees'.
    
    If no table from the list seems relevant, respond with the single word ERROR.

    User Prompt: "{user_question}"

    Table Name:
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        ai_response_raw = response.text.strip()
        
        # We still use our robust checking logic as a safety net.
        ai_response_lower = ai_response_raw.lower()
        for table in available_tables:
            if table.lower() == ai_response_lower:
                # This handles an exact (but case-insensitive) match
                print(f"AI identified table (exact match): {table}")
                return table
            if table.lower() in ai_response_lower:
                # This handles cases where the AI might add extra words
                print(f"AI identified table (partial match): {table}")
                return table
        
        # If no match was found after checking all tables
        print(f"AI response '{ai_response_raw}' did not match any known tables: {available_tables}")
        return None
            
    except Exception as e:
        print(f"Error identifying table name: {e}")
        return None


def classify_command_type(user_question):
    #Uses Gemini to classify the command as DDL, DML, or DQL.
    prompt = f"""
    Classify the following user command as one of four types: DDL_DATABASE, DDL_TABLE, DML, or DQL.
    - DDL_DATABASE: For commands that CREATE or DROP a database.
    - DDL_CREATE_TABLE: For commands that create a new table.
    - DDL_ALTER_TABLE: For commands that modify an existing table structure.
    - DDL_DROP_TABLE: For commands that delete an existing table.
    - DML: For commands that manage data within tables (INSERT, UPDATE, DELETE).
    - DQL_SHOW: For commands that list things within a database, like SHOW TABLES.
    - DQL: For general data retrieval from a specific table (SELECT).
    - SERVER_LEVEL_QUERY: For queries that run on the server, not in a specific database, like SHOW DATABASES.

    Your response must be a single word: DDL_DATABASE, DDL_CREATE_TABLE, DDL_ALTER_TABLE, DDL_DROP_TABLE, DML, DQL_SHOW, DQL, or SERVER_LEVEL_QUERY.

    User Command: "{user_question}"

    Classification:
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        classification = response.text.strip().upper()
        if classification in ["DDL_DATABASE", "DDL_CREATE_TABLE", "DDL_ALTER_TABLE", "DDL_DROP_TABLE", "DML", "DQL_SHOW", "DQL", "SERVER_LEVEL_QUERY"]:
            print(f"AI classified command as: {classification}")
            return classification
        return "UNKNOWN"
    except Exception as e:
        print(f"Error classifying command: {e}")
        return "UNKNOWN"

def get_sql_from_gemini(user_question, db_schema):

    # Generate SQL query using Gemini

    prompt = f"""
    You are a MySQL expert. Your task is to convert a natural language question into a single,
    executable MySQL query. You must only respond with the SQL query and nothing else.

    Given the following database schema:
    {db_schema}

    Convert this user question into a MySQL query: "{user_question}"

    MySQL Query:
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        sql_query = response.text.strip().replace("`", "").replace("sql", "")
        print("Successfully generated SQL query.")
        return sql_query
    except Exception as e:
        print(f"An error occurred while generating the SQL query: {e}")
        return None
