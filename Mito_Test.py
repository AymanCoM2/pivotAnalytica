import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pyodbc
import pandas as pd
import jwt
from mitosheet.public.v3 import *
from real import renderAlsoPivot

queryStringObject = st.experimental_get_query_params()
if (queryStringObject):
    tokenQuery = queryStringObject['name'][0]


def doThePivotCode(new_dfs, code):
    st.write(new_dfs)
    st.code(code)
    dataframes = list(new_dfs.keys())[1:]
    print()
    if st.button('Save Pivots'):
        with open("my_script.py", "w") as file:
            file.write(code)
            # file.write("dataframes = {}".format(list(new_dfs.keys())[1:]))

# ? 2
def renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCode):
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

    if True:
        renderAlsoPivot(dataFrame)
    else:
        new_dfs, code = spreadsheet(dataFrame, df_names=['dataFrame'])
        if (isAdmin):  # ! If Admin Give him Permission To see the "Save Button" For the Code
            doThePivotCode(new_dfs, code)


# ? 1
try:
    key = "simpleKey"
    aud = "urn:foo"
    alg = ["HS256"]
    resPonse = jwt.decode(tokenQuery, key, audience=aud, algorithms=alg)
    dbName = resPonse['dbName']
    dbSqlQuery = resPonse['sqlQuery']
    isAdmin = resPonse['isAdmin']
    pivotCode = resPonse['pivotCode']
    renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCode)
except Exception:
    # ExpiredSignatureError
    st.set_page_config(layout="wide")
    st.title('Access Denied')
    print("An exception occurred")
