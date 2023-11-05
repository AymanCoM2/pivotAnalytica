import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pyodbc
import pandas as pd
import jwt
from mitosheet.public.v3 import *
from my_script import renderAlsoPivot
import requests
import json


api_url = "http://10.10.10.66:8002/api/save-pivot"


queryStringObject = st.experimental_get_query_params()
if (queryStringObject):
    tokenQuery = queryStringObject['name'][0]


def writePivotIntoFile(pivotCode):
    with open("my_script.py", "w") as file:
        file.write(pivotCode)


def doThePivotCode(new_dfs, code, queryId):
    finalFile = ''
    st.write(new_dfs)
    st.code(code)
    dataframes = list(new_dfs.keys())[1:]
    fileContent = ''
    print()
    if st.button('Save Pivots'):
        with open("my_script.py", "w") as file:
            file.write('from mitosheet.streamlit.v1 import spreadsheet\n')
            file.write(code)
            file.write(
                'new_dfs, code = spreadsheet(dataFrame, dataFrame_pivot, df_names=[\'dataFrame\', \'dataFrame_pivot\'])\n')
        with open('my_script.py', 'r') as file:
            fileContent = file.read()
            data = {
                "fileContent": fileContent,
                "queryId": queryId,
            }
            json_data = json.dumps(data)
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url,  data=json_data, headers=headers)
            if response.status_code == 200:
                print("Request was successful.")
                response_data = json.loads(response.text)
                finalFile = response_data['fC']
            else:
                print("Request failed with status code:", response.status_code)
            with open("my_script.py", "w") as file:
                file.write(finalFile)


def renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCode, queryId):
    server = '10.10.10.100'
    database = dbName
    username = 'ayman'
    password = 'admin@1234'
    connection_string = f"DRIVER={{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.4.1}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    query_2 = (dbSqlQuery)
    st.set_page_config(layout="wide")
    st.title('MITO SHEET')
    dataFrame = pd.read_sql(query_2, connection)

    if pivotCode is not None:
        writePivotIntoFile(pivotCode)
        renderAlsoPivot(dataFrame)
    else:
        new_dfs, code = spreadsheet(dataFrame, df_names=['dataFrame'])
        if (isAdmin):  # ! If Admin Give him Permission To see the "Save Button" For the Code
            doThePivotCode(new_dfs, code, queryId)


# try:
#     key = "simpleKey"
#     aud = "urn:foo"
#     alg = ["HS256"]
#     resPonse = jwt.decode(tokenQuery, key, audience=aud, algorithms=alg)
#     dbName = resPonse['dbName']
#     dbSqlQuery = resPonse['sqlQuery']
#     isAdmin = resPonse['isAdmin']
#     pivotCode = resPonse['pivotCode']
#     queryId = resPonse['queryId']
#     renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCode, queryId)
# except Exception:
#     # ExpiredSignatureError
#     st.set_page_config(layout="wide")
#     st.title('Access Denied')
#     print("An exception occurred")
key = "simpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKeysimpleKey"
aud = "http://10.10.10.66:8052/"
alg = ["HS256"]
# resPonse = jwt.decode(tokenQuery, key, audience=aud, algorithms=alg)
resPonse = jwt.decode(tokenQuery, key, algorithms=alg,
                      audience=aud, options={"verify_exp": False},)
dbName = resPonse['dbName']
dbSqlQuery = resPonse['sqlQuery']
isAdmin = resPonse['isAdmin']
pivotCode = resPonse['pivotCode']
queryId = resPonse['queryId']
renderDataOnTable(dbName, dbSqlQuery, isAdmin, pivotCode, queryId)
