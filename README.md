Azure Open AI, Azure SQL LangChain Chatbot
The chatbot is designed to Integrate with Azure SQL Database, Azure Open Ai and Langchain API.

Prerequisite

1.  Azure Open AI Service with a deployment of Chat GRP 3.5 Turbo 16K
2.  Azure SQL Server Database or any datasource.  With Any Datasource, the code will have to change.
3.  SQL Server 2018 ODBC Client 
4.  Deply code to Visual Studio
5.  Run Requirments.txt
6. Fill in the .env file
    AZURE_OPENAI_API_KEY=""
    AZURE_OPENAI_ENDPOINT=""
    AZURE_OPENAI_MODEL_DEPLOYMENT=""
    AZURE_OPENAI_API_VERSION= ""
    AZURE_SQL_USER=""
    AZURE_SQL_PASSWORD=""
    AZURE_SQL_DB_NAME=""
    AZURE_SQL_SERVER=""
    AZURE_SHOW_SQL=True
    AZURE_VERBOSE=False
 7. Main Code is in Main.py
 8. Dockerfile include.
