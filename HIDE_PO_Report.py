#!/usr/bin/env python
# coding: utf-8

# In[20]:


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import io
import numpy as np
from flask import send_file
import dash_table
app = dash.Dash()
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import pandas as pd
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot, plot
from plotly.subplots import make_subplots
init_notebook_mode(connected=False)
from plotly import graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import date
from datetime import timedelta
from dash.dash import no_update
from dash.exceptions import PreventUpdate
import plotly_express as px
import dash_bootstrap_components as dbc
import pyodbc
import pandas as pd
pd.options.mode.chained_assignment=None
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from plotly.graph_objects import Layout
#import "DBCONN" db connection module -written by nag for sql server db connection
import DBCONN as dbconn
import sys
userid=sys.argv[1]


# In[2]:


cnx=dbconn.mydbconn("pds_sap_clone",'DbView','welcome@2020')


# In[3]:


stmt='''SELECT EBELN PO,COUNT(EBELN) 'PO Count',
case 
    when mtart ='YFGM' then 'GARMENT'
    when mtart ='ZFGM' then 'GARMENT' 
    when mtart ='ZTRM' then 'TRIMS'
    else 'FABRIC' 
end 'Vendor Type',
ELIKZ,
case 
	when (elikz = 'X' or ELIKZ = 'C' or ELIKZ ='D') then 'Closed'
	when (ELIKZ='' and (ELIKZ='C' OR ELIKZ='D' OR ELIKZ!='X') and [PO_STATUS]='A') then 'Accepted'
	when ((ELIKZ='' OR ELIKZ='C' OR ELIKZ='D' OR ELIKZ='X') and [PO_STATUS]='R') then 'Rejected'
	when ((Len(ELIKZ)=0 and ((CAST([SAP_PO_VER] AS int) - CAST([HID_PO_VER] AS int))=0) and [PO_STATUS]='')  
			or  ((Len(ELIKZ)=0 or ELIKZ='C' OR ELIKZ='D' OR ELIKZ='X') and ((CAST([SAP_PO_VER] AS int) - CAST([HID_PO_VER] AS int))>0) and ([PO_STATUS]='R' or [PO_STATUS]='A' ) OR [PO_STATUS]='')) then 'New'
	else 'Closed'
end 'Status',V_NAME1 'Supplier', PC_USER 'NL Merchandiser', PO_R_DATE 'PO Date' ,
EBELP 'PO Line Item',MENGE Quantity,ELIKZ 'hide_status', PO_STATUS 'PO Status',
WEMNG 'Shipped Quantity',OBMNG 'Balance Quantity',EINDT 'Last Delivery Date',
TXZ01 'Description',
LTRIM(RTRIM(CASE when [SAP_PO_VER] = '' then '0' else [SAP_PO_VER] end)) as SAP_PO_VER,
LTRIM(RTRIM(isnull([HID_PO_VER],'0'))) as HID_PO_VER, [PO_STATUS],T_ZTERM,Invno Invoice,
SUM(CAST(T_AMOUNT AS decimal(28,3))) 'Total Amount',lifnr 'Vendor'
FROM [dbo].[TB_PO_DETAILS] pot left outer join  dbo.exp_imp_invoice_details inv on pot.ebeln=inv.sappo
group by EBELN,ebelp,mtart,pc_user,C_NAME1 ,PO_STATUS ,V_NAME1 ,
MENGE ,wemng,obmng,ELIKZ ,EINDT,txz01,hid_po_ver,t_zterm,invno,PO_R_DATE,SAP_PO_VER,lifnr;
'''
report2=dbconn.runsql(stmt,cnx)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
report2.head(2)


# In[4]:


report2['Supplier']=report2['Supplier'].str.split(',',n=1,expand=True)
# A few columns values have "." and "-" as split, so splitting the data on "." and "-"
report2['Supplier']=report2['Supplier'].str.split('.',n=1,expand=True)
report2['Supplier']=report2['Supplier'].str.split('-',n=1,expand=True)

report2['Total Amount']=report2['Total Amount'].astype('float')
report2['PO']=report2['PO'].astype('int')
report2['Quantity']=report2['Quantity'].astype('float')

report2['Status'].unique()


# In[5]:



grouped_po=report2.groupby(['Vendor','Status'],as_index=False).PO.count()
grouped_po
grouped_total_amount=round(report2.groupby(['Vendor','Status'],as_index=False)['Total Amount'].sum(),2)
grouped_total_amount
grouped_quantity=round(report2.groupby(['Vendor','Status'],as_index=False)['Quantity'].sum(),2)
#grouped_quantity


# In[6]:


merged_df=grouped_po.merge(grouped_total_amount,on=['Vendor','Status'],how='outer').merge(grouped_quantity, on=['Vendor','Status'],how='outer')
#merged_df=merged_df.merge(report2[['Vendor Type','PO Status','PO Date']],on=['Vendor Type','PO Status'])


# In[7]:


po_statuses=merged_df['Status'].unique()
i=34
for vendor in merged_df['Vendor'].unique():
    for po_status in po_statuses:
            if (merged_df[(merged_df['Vendor']==vendor) & (merged_df['Status']==po_status)]['Status'].empty):
            #print(vendor,po_status)
                new_row={'Vendor':vendor,'Status':po_status,'PO':0,'Total Amount':0.0,'Quantity':0.0}
                merged_df=merged_df.append(new_row,ignore_index=True)
merged_df    


# In[8]:


merged_df.Status.value_counts()
df_for_graph=merged_df[merged_df['Vendor'].str.strip()==userid]


# In[9]:


df_for_graph


# In[21]:




fig=px.bar(data_frame=df_for_graph,x='Status',y='PO',hover_data=["Total Amount", "Quantity"],title="Purchase Order Status",
            width=600, height=400,color_discrete_map={"Accepted": "RebeccaPurple", "New": "MediumPurple", "Rejected": "DarkPurple", "Closed":"Purple"},template="simple_white")

#fig.show()
import plotly.io as pio
pio.write_html(fig, file='/Users/nagarajugooty/Downloads/po_report.html')


# In[18]:


layout = Layout(
    plot_bgcolor='rgba(0,0,0,0)',
    title='Purchase Order Status',
xaxis=dict(
    title='PO Status',
    titlefont=dict(
        family='Courier New, monospace',
        size=20,
        color='#7f7f7f'
    )
),
yaxis=dict(
    title='Count',
    titlefont=dict(
        family='Courier New, monospace',
        size=20,
        color='#7f7f7f'
    )
)
)
config={
"displaylogo": False
}
#layout=dict(title=dict(text="Purchase Order Status",xanchor='left'),marker_color='firebrick')



fig=go.Figure(data=px.bar(data_frame=df_for_graph,x='Status',y='PO',hover_data=["Total Amount", "Quantity"],color_discrete_map={"Accepted": "RebeccaPurple", "New": "MediumPurple", "Rejected": "DarkPurple", "Closed":"Purple"},template="simple_white"))

fig.update_layout(dict(autosize=False),
title={
'text': "Purchase Order Report",
'y':0.99,
'x':0.5,
'xanchor': 'center',
'yanchor': 'top'},
margin={'t': 50},
plot_bgcolor='rgba(0,0,0,0)',
#paper_bgcolor = 'lightgray',
showlegend=False, height=400,width=800)
fig.show()


# ## BPM Report

# In[ ]:




