from dotenv import load_dotenv
import streamlit as st
import os
import azure.functions as func
import logging
from langchain_openai import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.callbacks.base import BaseCallbackHandler
import pyodbc

#========.env file
load_dotenv()

keyvalue = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
apiversion = os.getenv("AZURE_OPENAI_API_VERSION")
chatdeployment  = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT")

userid = os.getenv("AZURE_SQL_USER") 
password = os.getenv("AZURE_SQL_PASSWORD") 
server = os.getenv("AZURE_SQL_SERVER") 
dbname = os.getenv("AZURE_SQL_DB_NAME")
showsql = os.getenv("AZURE_SHOW_SQL")

verbose = os.getenv("AZURE_VERBOSE")


if verbose is True:
    verbosebool = True
else:
    verbosebool = False

uri = 'mssql+pyodbc://'+userid+':'+password + "@" +server + '/' + dbname + '?driver=ODBC+Driver+18+for+SQL+Server'

db = SQLDatabase.from_uri(uri)


#=======================  SQL Handler
class SQLHandler(BaseCallbackHandler):
    def __init__(self):
        self.sql_result = []

    def on_agent_action(self, action, **kwargs):
        """Run on agent action. if the tool being used is sql_db_query,
         it means we're submitting the sql and we can 
         record it as the final sql"""

        if action.tool in ["sql_db_query_checker","sql_db_query"]:
            self.sql_result.append(action.tool_input)


#==========================Generate the response from open ai and SQL
def generate_response(input_text):

    logging.info('Azure Chat Open AI Opened')
    llm = AzureChatOpenAI(
    azure_deployment = chatdeployment,
    azure_endpoint = endpoint,
    openai_api_version = apiversion,
    temperature = 0)

    handler = SQLHandler()
    agent_executor = create_sql_agent(llm, db=db,
           agent_type="openai-tools", 
           verbose=verbosebool, 
           max_execution_time=10000, 
           handle_parsing_errors=True, 
           handle_sql_errors=True)
    
    sql_queries = handler.sql_result
        
        
    results = agent_executor.invoke({'input':input_text},{'callbacks':[handler]})
    yield results['output']
    if sqloutput == "ON":
        yield sql_queries
###########################################################

def list_Tables(tablesdict):
    
    output = "\r\r"

    for tableitem in tablesdict:
        output = output + tableitem + " \r\r"

    return output


def init_system_prompt():
    return [
    {"role":"system", "content":f"""You are a helpful AI data analyst assistant who can answer questions about a SQL database, 
     You can execute SQL queries to retrieve information from a sql database,
     The database is SQL server, use the right syntax to generate sql queries


    Question: "What is the percentage males to females in the persons table?"
    Answer: "The percentage of females to males in the persons table is approximately 16.2% females and 83.8% males."
    Query: "SELECT COUNT(*) AS TotalCount, SUM(CASE WHEN Sex = 'F' THEN 1 ELSE 0 END) AS FemaleCount, SUM(CASE WHEN Sex = 'M' THEN 1 ELSE 0 END) AS MaleCount FROM Persons" 

    
     """} ]

#    Think step by step, before doing anything, share the different steps you'll execute to get the answer


system_prompt = init_system_prompt()
st.set_page_config(page_title="Azure SQL Agent", layout="wide")

st.title("Bureau of International Narcotic Law Enforcement")

st.info("Training Data Chat Bot Prompts:", icon="📃")
st.info(system_prompt[0]["content"], icon="📃")

with st.sidebar:
    sqloutput = st.radio(
        "Choose On or Off for SQL Output",
        ("OFF", "ON")
    )

with st.sidebar:
    chatdeployment = st.radio(
        "Choose one of the LLMs",
        ("gpt-35-turbo-16k", "gpt-4.1-mini","gpt-4o")
    )


with st.sidebar.expander('Availabe Database Tables', expanded=True):
            st.write( '\n- '.join(db.get_usable_table_names()))


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me Question regarding the tables."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner('Working on it'):
            response = st.write_stream(generate_response(prompt))
            st.success("Done!")
       # Add assistant response to chat history

    st.session_state.messages.append({"role": "assistant", "content": response})
    