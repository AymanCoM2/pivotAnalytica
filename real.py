from mitosheet.public.v3 import *
from mitosheet.streamlit.v1 import spreadsheet
from mitosheet.public.v3 import *


def renderAlsoPivot(dataFrame):
    tmp_df = dataFrame[['LWhs', 'ItemCode', 'WhsCode']].copy()
    pivot_table = tmp_df.pivot_table(
        index=['LWhs'],
        columns=['ItemCode'],
        values=['WhsCode'],
        aggfunc={'WhsCode': ['count']}
    )
    pivot_table = pivot_table.set_axis(
        [flatten_column_header(col) for col in pivot_table.keys()], axis=1)
    dataFrame_pivot = pivot_table.reset_index()
    new_dfs, code = spreadsheet(dataFrame, dataFrame_pivot, df_names=[
                                'dataFrame', 'dataFrame_pivot'])
