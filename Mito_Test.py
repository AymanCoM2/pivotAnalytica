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
        file.write(pivotCodeList)


def renderWithNewPivotCode(new_dfs, code, queryId, userId):
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
            api_url = "http://127.0.0.1:8000/api/save-pivot"
            response = requests.post(api_url,  data=json_data, headers=headers)
            if response.status_code == 200:
                print("Request was successful.")
            else:
                print("Request failed with status code:", response.status_code)

def renderDataOnTable(dbName, sqlQuery, pivotCode, queryId, userId, isForSavingNewPivot):
    # server = '10.10.10.100'
    server = 'jou.is-by.us'
    database = dbName
    username = 'ayman'
    password = 'admin@1234'
    # !@ Port is Very important
    connection_string = f"DRIVER={{SQL Server}};SERVER={server},443;DATABASE={database};UID={username};PWD={password}"
    # connection_string = f"DRIVER={{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.4.1}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    # connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER="+server + \
    #     "," + "443"+";"+"DATABASE=" + database + \
    #     ";UID=" + username + ";PWD=" + password
    connection = pyodbc.connect(connection_string)
    query_2 = (sqlQuery)
    st.set_page_config(layout="wide")
    st.title('MITO SHEET')
    dataFrame = pd.read_sql(query_2, connection)
    if pivotCode:
        writePivotIntoFile(pivotCode)
        # ! Above is Useless Code , Just Writing it to know it
        exec_globals = {'dataFrame': dataFrame}
        exec(pivotCode, exec_globals)
    elif (isForSavingNewPivot):
        new_dfs, code = spreadsheet(dataFrame, df_names=['dataFrame'])
        renderWithNewPivotCode(new_dfs, code, queryId, userId)

# & Here you get the UUID and If It is Not Used you Render the new Table For it 
def secondStepGetUUIData(innerUUID):
    endPoint = "http://127.0.0.1:8000/api/get-uuid-data"
    data = {
        "uuid": innerUUID,
    }
    json_data = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    response = requests.post(endPoint,  data=json_data, headers=headers)
    if response.status_code == 200:
        print("Request was successful.")
        tempObject = response.json()
        isUsed = tempObject['isUsed']
        if (isUsed):
            print('is Used')
            raise ValueError("Key Is Used")
        else:
            isForSavingNewPivot = tempObject['isForSavingNewPivot']
            user_id = tempObject['user_id']
            query_id = tempObject['query_id']
            pivotCode = tempObject['pivotCode']
            sqlQuery = tempObject['sqlQuery']
            dbName = tempObject['dbName']
            renderDataOnTable(dbName, sqlQuery, pivotCode,
                              query_id, user_id, isForSavingNewPivot)
    else:
        print("Request failed with status code:", response.status_code)

# & Here you Get the UUID Then If you Get it , You Send It to Another Function 
def firstStepGetUUID():
    try:
        queryStringObject = st.experimental_get_query_params()
        if (queryStringObject):
            insertedUUID = queryStringObject['name'][0]
        secondStepGetUUIData(insertedUUID)
    except Exception:
        print(None)


firstStepGetUUID()
# except Exception:
#     st.set_page_config(layout="wide")
#     st.title('Access Denied')
#     print("An exception occurred")
