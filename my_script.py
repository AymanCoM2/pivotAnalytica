from mitosheet.streamlit.v1 import spreadsheet
from mitosheet.public.v3 import *
def renderAlsoPivot(dataFrame):
	# Pivoted dataFrame into dataFrame_pivot
	tmp_df = dataFrame[['WhsCode', 'STOCK']].copy()
	pivot_table = tmp_df.pivot_table(
	    index=['STOCK'],
	    values=['WhsCode'],
	    aggfunc={'WhsCode': ['count']}
	)
	pivot_table = pivot_table.set_axis([flatten_column_header(col) for col in pivot_table.keys()], axis=1)
	dataFrame_pivot = pivot_table.reset_index()
	
	# Pivoted dataFrame into dataFrame_pivot_1
	tmp_df = dataFrame[['WhsCode']].copy()
	pivot_table = tmp_df.pivot_table(
	    index=['WhsCode'],
	    values=['WhsCode'],
	    aggfunc={'WhsCode': ['count']}
	)
	pivot_table = pivot_table.set_axis([flatten_column_header(col) for col in pivot_table.keys()], axis=1)
	dataFrame_pivot_1 = pivot_table.reset_index()
	new_dfs, code = spreadsheet(dataFrame,dataFrame_pivot,dataFrame_pivot_1, df_names=['dataFrame', 'dataFrame_pivot', 'dataFrame_pivot_1'])
renderAlsoPivot(dataFrame)
