# **Cognita 🧠**

**Query Made Human.** Cognita is an intelligent web application that translates natural language commands into executable MySQL queries. It serves as a powerful, user-friendly interface for interacting with databases, removing the need to write complex SQL code manually.

Built with Python, Streamlit, and the Google Gemini API, Cognita can understand and execute a wide range of database operations, from simple data retrieval to complex table modifications and definitions.

## **✨ Core Features**

* **Natural Language to SQL:** Ask questions or give commands in plain English. 
* **Full Spectrum SQL Support:**  
   * **Server-Level Queries:** `SHOW DATABASES`

   * **DDL (Data Definition Language):** `CREATE`, `ALTER`, `DROP`

   * **DML (Data Manipulation Language):** `INSERT`, `UPDATE`, `DELETE`
   * **DQL (Data Query Language):** `SELECT`, `SHOW TABLES`
* **Intelligent, Multi-Step AI Pipeline:** Uses a sophisticated workflow to ensure commands are understood correctly and executed in the proper context.
* **Dynamic Schema Awareness:** Automatically discovers tables in the database and fetches the relevant table's structure to provide context to the AI, ensuring highly accurate queries.  
* **Interactive UI:** A clean and modern user interface built with Streamlit, featuring a Catppuccin-inspired theme.

## **🚀 How It Works: The Intelligent Pipeline**

Cognita doesn't just make a single, naive call to an AI. It follows a robust, multi-step process to ensure accuracy and safety, making it a truly intelligent assistant.

1. **AI Command Classification:** First, the user's prompt is sent to the Gemini API to classify the command type. This determines the entire workflow.  
2. **AI-Driven Connection Strategy:** Based on this precise classification, the app intelligently decides how to connect to the MySQL server:

   * For server-level commands (`SERVER_LEVEL_QUERY`, `DDL_DATABASE`), it connects to the server without requiring a specific database name.

   * For all other commands, it requires a database name from the user and connects directly to it.

3. **Context-Aware Execution Path:** The app then follows a specific logic path tailored to the command type:
   * Server-Level Path: For commands like SHOW DATABASES, the app generates and executes the SQL directly.

   * Create Table Path: For CREATE TABLE commands, the app bypasses table discovery (as none may exist) and generates the SQL directly, solving the "empty database" problem.

   * Context-Dependent Path: For all other table-level commands (ALTER, DROP, DML, DQL), the app executes its full discovery pipeline:

      1.  Fetches a list of all available tables in the database.

      2.  Asks the AI to identify the target table from the user's prompt, using the discovered list as a set of valid options.

      3. Fetches the specific schema (column names and data types) for the identified table.

      4. Generates the final, context-aware SQL query using this schema.

4. **Execution & Display:** The final, validated query is executed against the database, and the results (data, row count, or a success message) are displayed to the user.

## **🛠️ Technology Stack**

* **Backend:** Python  
* **Frontend:** Streamlit  
* **Database:** MySQL (connected via mysql-connector-python)  
* **AI Model:** Google Gemini API (google-generativeai)  

## **⚙️ Setup and Installation**

Follow these steps to get Cognita running on your local machine.

### **Prerequisites**

* Python 3.8+  
* MySQL Server installed and running.  
* A Google Gemini API Key.

### **Installation Steps**

1. **Clone the repository:**  
    ```
    git clone https://github.com/abhnva/cognita.git 
    cd cognita
    ```

2. **Create a virtual environment (recommended):**  
   ```
   python \-m venv venv  
   source venv/bin/activate  \# On Windows, use \`venv\\Scripts\\activate\`
   ```

3. **Install the required libraries:**  
   ```
   pip install -r requirements.txt
   ```

4. **Set up your environment variables:**  
   Create a file named .env in the root of your project folder and add your credentials:  
   ```
   GOOGLE_API_KEY="your-google-gemini-api-key"
   ```  

5. **Run the application:**  
   ```
   streamlit run app.py
   ```

   The application should open in your default web browser.

## **Usage**

1. Enter the name of the database you wish to connect to in the sidebar.  
2. Type your command or question in the text area.  
3. Click "Execute Command".

### **Example Prompts**

* **DQL:** Show the names and wages of all workers from the worker table.  
* **DML:** Insert a new record into the students table with name 'Rohan' and marks 95 in class 11\.  
* **DDL:** Create a new table called 'projects' with an id (integer) and a project\_name (varchar).

## **👤 Author**

* **abhnv** \- [GitHub](https://github.com/abhnva)

## **📄 License**

This project is licensed under the MIT License.