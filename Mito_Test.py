import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pyodbc
import pandas as pd
import jwt
from mitosheet.public.v3 import *
import requests
import json
import re
from streamlit.components.v1 import html
from IPython.display import display, Javascript

# api_url = "http://10.10.10.66:8002/api/save-pivot"
api_url = "http://127.0.0.1:8000/api/save-pivot"
queryStringObject = st.experimental_get_query_params()
if (queryStringObject):
    tokenQuery = queryStringObject['name'][0]


def handleOneOrBulkPivots(codeString):
    pivot_lines = re.findall(
        r'# Pivoted dataFrame into (dataFrame_pivot|\S+_\d*)', codeString)
    df_names = []
    for i, name in enumerate(pivot_lines):
        if i == 0:
            df_names.append('dataFrame_pivot')
        else:
            df_names.append(f'dataFrame_pivot_{i}')
    df_names.insert(0, 'dataFrame')
    output_string = "new_dfs, code = spreadsheet({0}, df_names={1})\n".format(
        ','.join(df_names), str(df_names))
    return output_string


def writePivotIntoFile(pivotCodeList):
    with open("my_script.py", "w") as file:
        # This is a List so you Will need to Parse Later
        file.write(pivotCodeList)


def doThePivotCode(new_dfs, code, queryId, userId):
    st.write(new_dfs)
    st.code(code)
    dataframes = list(new_dfs.keys())[1:]
    fileContent = ''
    if st.button('Save Pivots'):
        with open("my_script.py", "w") as file:
            file.write('from mitosheet.streamlit.v1 import spreadsheet\n')
            file.write(code)
            lastLineOfCode = handleOneOrBulkPivots(code)
            # file.write('new_dfs, code = spreadsheet(dataFrame, dataFrame_pivot, df_names=[\'dataFrame\', \'dataFrame_pivot\'])\n')
            file.write(lastLineOfCode)
        with open('my_script.py', 'r') as file:
            fileContent = file.read()
            data = {
                "fileContent": fileContent,
                "queryId": queryId,
                "userId": userId
            }
            json_data = json.dumps(data)
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url,  data=json_data, headers=headers)
            if response.status_code == 200:
                print("Request was successful.")
            else:
                print("Request failed with status code:", response.status_code)


def renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCodeList, queryId, userId):
    # server = '10.10.10.100'
    server = 'jou.is-by.us'
    database = dbName
    username = 'ayman'
    password = 'admin@1234'
    # !@ Port is Very important to do this Connection
    connection_string = f"DRIVER={{SQL Server}};SERVER={server},443;DATABASE={database};UID={username};PWD={password}"
    # connection_string = f"DRIVER={{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.4.1}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    query_2 = (dbSqlQuery)
    # st.set_page_config(layout="wide")
    st.title('MITO SHEET')
    dataFrame = pd.read_sql(query_2, connection)
    if pivotCodeList:
        # ! This is Userless Code , Just Writing it to know it
        writePivotIntoFile(pivotCodeList)
        # ! Here will be a loop Over the Codes To make ALL pivots One By One
        exec_globals = {'dataFrame': dataFrame}
        exec(pivotCodeList, exec_globals)
    else:
        new_dfs, code = spreadsheet(dataFrame, df_names=['dataFrame'])
        doThePivotCode(new_dfs, code, queryId, userId)


try:
    key = "simpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKey"
    aud = "2coomdashboard"
    alg = ["HS256"]
    resPonse = jwt.decode(tokenQuery, key, algorithms=alg,
                          audience=aud, options={"verify_exp": False},)
    queryId = resPonse['queryId']
    dbName = resPonse['dbName']
    dbSqlQuery = resPonse['sqlQuery']
    pivotCodeList = resPonse['pivotCode']
    isAdmin = resPonse['isAdmin']
    userId = resPonse['userId']

    print('///////////////////////////////////')
    print(pivotCodeList)
    renderDataOnTable(dbName, dbSqlQuery, isAdmin,
                      pivotCodeList, queryId, userId)
except Exception:
    # ExpiredSignatureError
    st.set_page_config(layout="wide")
    st.title('Access Denied')
    print("An exception occurred")


# key = "simpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKey"
# aud = "2coomdashboard"
# alg = ["HS256"]
# resPonse = jwt.decode(tokenQuery, key, algorithms=alg,
#                       audience=aud, options={"verify_exp": False},)
# queryId = resPonse['queryId']
# dbName = resPonse['dbName']
# dbSqlQuery = resPonse['sqlQuery']
# pivotCodeList = resPonse['pivotCode']
# isAdmin = resPonse['isAdmin']
# userId = resPonse['userId']

# renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCodeList, queryId, userId)
