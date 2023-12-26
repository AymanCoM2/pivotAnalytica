import streamlit as st
from mitosheet.streamlit.v1 import spreadsheet
import pyodbc
import pandas as pd
from mitosheet.public.v3 import *
import requests
import json
import re


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


def renderWithNewPivotCode(new_dfs, code, queryId, userId, innerUUID):
    fileContent = ''
    st.code(code)
    if st.button('Save Pivots'):
        with open("my_script.py", "w") as file:
            file.write('from mitosheet.streamlit.v1 import spreadsheet\n')
            file.write(code)
            lastLineOfCode = handleOneOrBulkPivots(code)
            file.write(lastLineOfCode)
        with open('my_script.py', 'r') as file:
            fileContent = file.read()
            data = {
                "fileContent": fileContent,
                "queryId": queryId,
                "userId": userId,
                "originalCode": code
            }
            json_data = json.dumps(data)
            headers = {"Content-Type": "application/json"}
            api_url = "https://jou.mine.nu:8010/api/save-pivot"
            response = requests.post(api_url,  data=json_data, headers=headers)
            if response.status_code == 200:
                print("Request was successful.")
            else:
                print("Request failed with status code:", response.status_code)


def renderDataOnTable(dbName, sqlQuery, pivotCode, queryId, userId, isForSavingNewPivot, innerUUID, originalCode):
    server = 'jou.is-by.us'
    database = dbName
    username = 'ayman'
    password = 'admin@1234'
    # !@ Port is Very important
    # connection_string = f"DRIVER={{SQL Server}};SERVER={server},443;DATABASE={database};UID={username};PWD={password}"
    connection_string = f"DRIVER={{/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.5.1}};SERVER={server},443;DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    query_2 = (sqlQuery)
    st.set_page_config(layout="wide")
    st.header('جدول التقارير')
    dataFrame = pd.read_sql(query_2, connection)
    if pivotCode:
        writePivotIntoFile(pivotCode)
        # ! Above is Useless Code,Just Writing it to know it
        exec_globals = {'dataFrame': dataFrame}
        exec(pivotCode, exec_globals)
    elif (isForSavingNewPivot):
        new_dfs, code = spreadsheet(dataFrame, df_names=['dataFrame'])
        renderWithNewPivotCode(new_dfs, code, queryId, userId, innerUUID)


def secondStepGetUUIData(innerUUID):
    endPoint = "https://jou.mine.nu:8010/api/get-uuid-data"
    data = {
        "uuid": innerUUID,
    }
    json_data = json.dumps(data)
    headers = {"Content-Type": "application/json"}
    response = requests.post(endPoint,  data=json_data, headers=headers)
    if response.status_code == 200:
        print("secondStepGetUUIData Request.")
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
            originalCode = tempObject['original']
            renderDataOnTable(dbName, sqlQuery, pivotCode, query_id,
                              user_id, isForSavingNewPivot, innerUUID, originalCode)
    else:
        print("Request failed with status code:", response.status_code)


def firstStepGetUUID():
    try:
        queryStringObject = st.experimental_get_query_params()
        if (queryStringObject):
            insertedUUID = queryStringObject['name'][0]
        secondStepGetUUIData(insertedUUID)
    except Exception:
        print(None)


firstStepGetUUID()
