import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pyodbc
import pandas as pd
import jwt

queryStringObject = st.experimental_get_query_params()
tokenQuery = queryStringObject['name'][0]
print(tokenQuery)
# !  http://localhost:8501/?name=ayman
# & {'name': ['ayman']}


def renderDataOnTable(dbName, dbSqlQuery):
    server = '10.10.10.100'
    database = dbName
    username = 'ayman'
    password = 'admin@1234'
    connection_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    query_2 = (dbSqlQuery)

    st.set_page_config(layout="wide")
    st.title('MITO SHEET')

    dataFrame = pd.read_sql(query_2, connection)

    new_dfs, code = spreadsheet(dataFrame, df_names=['dataFrame'])


try:
    resPonse = jwt.decode(tokenQuery, "simpleKey",
                          audience="urn:foo", algorithms=["HS256"])
    print("Res = ")
    print(resPonse)
    dbName = resPonse['dbName']
    dbSqlQuery = resPonse['sqlQuery']
    renderDataOnTable(dbName, dbSqlQuery)
except Exception:
    # raise ExpiredSignatureError("Signature has expired")
    print("An exception occurred")


# Get the Query String From the URL
# It is a JWT so you Need to parse it
# It has a Timing and Expires , If it is Valid , Make the API reuqset and Build it
# else Show a 404 error page and Close Everything


# st.write(new_dfs)
# st.code(code)

# dataframes = list(new_dfs.keys())[1:]
# print()
# if st.button('Save Pivots'):
#     with open("my_script.py", "w") as file:
#         file.write(code)
#         file.write("dataframes = {}".format(list(new_dfs.keys())[1:]))
