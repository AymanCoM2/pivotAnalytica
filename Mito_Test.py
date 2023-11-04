import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pyodbc
import pandas as pd
import jwt
from mitosheet.public.v3 import *


queryStringObject = st.experimental_get_query_params()
if (queryStringObject):
    tokenQuery = queryStringObject['name'][0]


def doThePivotCode(new_dfs, code):
    st.write(new_dfs)
    st.code(code)
    dataframes = list(new_dfs.keys())[1:]
    print()
    if st.button('Save Pivots'):  # ! This Name For Button Is Made by programmer
        with open("my_script.py", "w") as file:
            file.write(code)
            # file.write("dataframes = {}".format(list(new_dfs.keys())[1:]))


# ? 2
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



    # ! --->
    if True:
        tmp_df = dataFrame[['ItemName', 'RWhs']].copy()
        pivot_table = tmp_df.pivot_table(
            index=['ItemName'],
            columns=['ItemName'],
            values=['RWhs'],
            aggfunc={'RWhs': ['count']}
        )
        pivot_table = pivot_table.set_axis(
            [flatten_column_header(col) for col in pivot_table.keys()], axis=1)
        dataFrame_pivot = pivot_table.reset_index()
    # ! --->

    
    new_dfs, code = spreadsheet(dataFrame , dataFrame_pivot, df_names=['dataFrame' , 'dataFrame_pivot'])
    doThePivotCode(new_dfs, code)


# ? 1
try:
    key = "simpleKey"
    aud = "urn:foo"
    alg = ["HS256"]
    resPonse = jwt.decode(tokenQuery, key, audience=aud, algorithms=alg)
    dbName = resPonse['dbName']
    dbSqlQuery = resPonse['sqlQuery']
    renderDataOnTable(dbName, dbSqlQuery)
except Exception:
    # ExpiredSignatureError
    st.set_page_config(layout="wide")
    st.title('Access Denied')
    print("An exception occurred")
