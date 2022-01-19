#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


cnx=dbconn.mydbconn("hide_clone",'DbView','welcome@2020')


# In[ ]:





# ## BPM Report

# In[ ]:





# In[3]:


def get_bpm_df(status,sp_arg):
    if status=='open':
        sql="exec hide_clone.dbo.CB_SP_SelectBPMOpenTabDetails ?,?,?,?,?"
    elif status=='wip':
        sql="exec hide_clone.dbo.CB_SP_SelectBPMWIPTabList ?,?,?,?,?,?" 
    elif status=='closed':
        sql="exec hide_clone.dbo.[CB_SP_SelectBPMClosedTabList] ?,?,?,?" 
    elif status=='exception':
        sql="exec hide_clone.dbo.CB_SP_SelectBPMExceptionTabList ?,?"
    else:
        None
    args=sp_arg
    cursor=cnx.cursor()
    result=cursor.execute(sql,(args)).fetchall()
    cols=[column[0] for column in cursor.description]
    df=pd.DataFrame((tuple(t) for t in result),columns=cols) 
    cursor.close()
    return df


# In[4]:


import datetime
def set_due_date(df):
    new_date=[]
    for i in range(len(df)):
        days=df.stageDays[i].tolist()
        new_date.append(df.start_date[i]+datetime.timedelta(days=days))
 #   print(df.dueDate[i],' - ', df.start_date[i])
    df['dueDate']=new_date
    return df


# In[5]:


#open BPM
#args=('Internal',363,0,0,1)
args=('Internal',userid,0,0,1)

open_bpm_df=get_bpm_df('open',args)
open_bpm_df=set_due_date(open_bpm_df)
open_bpm_df.shape


# In[6]:


#wip BPM
#args=('Internal',363,0,0,0,1)
args=('Internal',userid,0,0,0,1)
wip_bpm_df=get_bpm_df('wip',args)
wip_bpm_df=set_due_date(wip_bpm_df)
wip_bpm_df.shape


# In[7]:


#closed BPM
#args=('Internal',363,1,1)
args=('Internal',userid,1,1)
closed_bpm_df=get_bpm_df('closed',args)
closed_bpm_df=set_due_date(closed_bpm_df)
closed_bpm_df.shape


# In[8]:


#exception BPM
#args=('Internal',363)
args=('Internal',userid)
exception_bpm_df=get_bpm_df('exception',args)
exception_bpm_df=set_due_date(exception_bpm_df)
exception_bpm_df.shape


# In[9]:


#Merge all BPM DFs. Exception is having different number of columns
merged_df=pd.merge(open_bpm_df,wip_bpm_df,how='outer')
merged_df=pd.merge(merged_df,closed_bpm_df,how='outer')
merged_df.shape


# In[10]:


#merged_df.info()
vendor_status=['Open','WIP','Closed','Exception']
vendor_status_values=[open_bpm_df.isOpen.count(),wip_bpm_df.isWip.count(),closed_bpm_df.isClosed.count(),exception_bpm_df.isOnHold.count()]


# In[11]:


#function for data_table
def create_data_table(df):
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'

#fig2 = go.Figure(data=[go.Table(
    data_table=go.Table(
      header=dict(
        values=[cols for cols in df.columns],

    line_color='darkslategray',
    fill_color=headerColor,
    align=['center'],
    font=dict(color='white', size=12)
      ),
      cells=dict(
    values=[df[k].tolist() for k in df.columns[0:]],
      line_color='darkslategray',
    # 2-D list of colors for alternating rows
    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
    align = ['left'],
    font = dict(color = 'darkslategray', size = 11),height=60
    ))
    #display(df.head())
    
    return data_table


# In[12]:


def draw_graph(trace,filename):
    fig=go.Figure(data=trace)
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
    showlegend=False, height=300,width=600)
    pio.write_html(fig, file='/Users/nagarajugooty/Downloads/'+filename)
    #fig.show()
    return fig


# In[13]:


#WIP BPM Report
if wip_bpm_df.size > 0:
    trace=create_data_table(wip_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
    #wip_bpm_graph=draw_graph(trace,'wip_bpm_report.html')
    wip_bpm_graph=create_data_table(wip_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
#Open BPM Report
if open_bpm_df.size > 0:
    trace=create_data_table(open_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
    #open_bpm_graph=draw_graph(trace,'open_bpm_report.html')
    open_bpm_graph=create_data_table(open_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
#Closed BPM Report
if closed_bpm_df.size > 0:
    trace=create_data_table(closed_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
    #closed_bpm_graph=draw_graph(trace,'closed_bpm_report.html')
    closed_bpm_graph=create_data_table(closed_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
#Exception BPM Report
if exception_bpm_df.size > 0:
    trace=create_data_table(exception_bpm_df[['SLNO','threadID','ThrdRef','stageName','stageDescription','RASCI','peopleInfo','start_date', 'dueDate']])
    exception_bpm_graph=draw_graph(trace,'exception_bpm_report.html')


# In[14]:


merged_df.groupby('isOpen')['start_date']


# ### trying Dash

# In[15]:


app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

res_ad = False

datatable=dash_table.DataTable(
    id='open_table',
    columns=[{"name": i, "id": i} for i in open_bpm_df.columns],
    data=open_bpm_df.to_dict("rows"),
    style_table={
                'maxHeight': '170px',
                'overflowY': 'scroll',
                'padding-left': '20px',
                'width': '1250px',
            },
     style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'border': '1px solid black'
    }
    #data=report2.to_dict("rows"),
)

today=pd.to_datetime(date.today())

today_val=open_bpm_df[(pd.to_datetime(open_bpm_df['dueDate'])-pd.to_datetime("now"))//np.timedelta64(1, 'D')==0]['dueDate'].count()
tomorrow_val=open_bpm_df[(pd.to_datetime(open_bpm_df['dueDate'])-pd.to_datetime("now"))//np.timedelta64(1, 'D')==1]['dueDate'].count()
dayafter_val=open_bpm_df[(pd.to_datetime(open_bpm_df['dueDate'])-pd.to_datetime("now"))//np.timedelta64(1, 'D')==2]['dueDate'].count()

#dummy values for layout display - have to remove
#today_val=15
#tomorrow_val=23
#dayafter_val=17

today_fig= go.Figure()
today_fig.update_layout(
    autosize=True,
    paper_bgcolor="LightGrey",
    margin=dict(
        l=30,
        r=30,
        b=0,
        t=0
    ),
)

today_fig.add_trace(go.Indicator(
    mode = "gauge+number",
    value = today_val,
    title = {'text': "Due Today"},
    domain = {'x': [0, 1], 'y': [0, 1]}
))

tomorrow_fig= go.Figure()
tomorrow_fig.add_trace(go.Indicator(
    mode = "gauge+number",
    value = tomorrow_val,
    title ={'text': "Due Tomorrow"},
    domain = {'x': [0, 1], 'y': [0, 1]}
))
tomorrow_fig.update_layout(
    autosize=True,
    paper_bgcolor="LightGrey",
    margin=dict(
        l=30,
        r=30,
        b=0,
        t=0
    ),
)

dayafter_fig=go.Figure()
dayafter_fig.add_trace(go.Indicator(
    mode = "gauge+number",
    value = dayafter_val,
    title ={'text': "Due Day After"},
    domain = {'x': [0, 1], 'y': [0, 1]}
))
dayafter_fig.update_layout(
    autosize=True,
    paper_bgcolor="LightGrey",
    margin=dict(
        l=30,
        r=30,
        b=0,
        t=0
    ),
)

bar_fig=go.Figure()
bar_fig.add_trace(go.Bar(x=vendor_status,y=vendor_status_values))
bar_fig.update_layout(
    autosize=True,
    paper_bgcolor="LightGrey",
    plot_bgcolor='beige',
    margin=dict(
        l=10,
        r=5,
        b=0,
        t=0
    ),
)

'''greenyellow, honeydew, hotpink, indianred, indigo,
            ivory, khaki, lavender, lavenderblush, lawngreen,
            lemonchiffon, lightblue, lightcoral, lightcyan,
            lightgoldenrodyellow, lightgray, lightgrey,
            lightgreen, lightpink, lightsalmon, lightseagreen,
            lightskyblue, lightslategray, lightslategrey,
            lightsteelblue, lightyellow, lime, limegreen,'''

scatter_fig=go.Figure()
scatter_fig.add_trace(go.Scattergl(x=merged_df.start_date, y=merged_df.isOpen,mode='markers+lines',marker = dict(line = dict(width = 1,color = 'darkslategrey'))))
scatter_fig.update_layout(
    autosize=True,
    paper_bgcolor="LightGrey",
    plot_bgcolor='beige',
    margin=dict(
        l=20,
        r=10,
        b=0,
        t=0
    ),
)

#Pie Chart
pie_fig=go.Figure()
pie_fig.add_trace(go.Pie(labels=vendor_status,values=vendor_status_values))
pie_fig.update_layout(
    autosize=True,
    paper_bgcolor="LightGrey",
    margin=dict(
        l=20,
        r=10,
        b=0,
        t=0
    ),
)

today_graph = dcc.Graph(id='today_indicator', figure=today_fig,style={"height": "220px", "width": "310px",'padding-left': '5px'})
tomorrow_graph = dcc.Graph(id='tomorrow_indicator', figure=tomorrow_fig, style={"height": "220px", "width": "310px"})
dayafter_graph = dcc.Graph(id='dayafter_indicator', figure=dayafter_fig, style={"height": "220px", "width": "310px"})
bar_graph = dcc.Graph(id='bar_chart', figure=bar_fig, style={"height": "200px", "width": "650px"})
scatter_graph=dcc.Graph(id='scatter_graph',figure=scatter_fig,style={"height": "200px", "width": "600px",'padding-left': '20px'})
data_table=dcc.Graph(id='data_table',figure=datatable)
pie_chart = dcc.Graph(id='pie_graph', figure=pie_fig, style={"height": "220px", "width": "304px"})

#Dash
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
app.title = "HID-e Dashboard"
app.config['suppress_callback_exceptions'] = True
server = app.server

body = dbc.Container([
        dbc.Row([html.H2("Vendor Dashboard",id='heading')],justify='center'),
        dbc.Row([today_graph,tomorrow_graph,dayafter_graph,pie_chart],no_gutters=True,justify='left'),
        dbc.Row([scatter_graph, bar_graph]),
        dbc.Row([datatable])
    ],
    className="mt-4",
    fluid=True
)

app.layout = html.Div([body])
if __name__ == "__main__":
    app.run_server()


# In[ ]:





# In[16]:


fig=px.bar(data_frame=df_for_graph,x='Status',y='PO',hover_data=["Total Amount", "Quantity"],title="Purchase Order Status",
            width=600, height=400,color_discrete_map={"Accepted": "RebeccaPurple", "New": "MediumPurple", "Rejected": "DarkPurple", "Closed":"Purple"},template="simple_white")

#fig.show()
import plotly.io as pio


# In[ ]:


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
pio.write_html(fig, file='/Users/nagarajugooty/Downloads/po_report.html')
#fig.show()


# In[ ]:





# In[ ]:


#today_val=open_bpm_df[(open_bpm_df['dueDate']-today)/np.timedelta64(1, 'D')==0.0]
#tomorrow_val=open_bpm_df[(open_bpm_df['dueDate']-today)/np.timedelta64(1, 'D')==1.0]['dueDate'].count()
#dayafter_val=open_bpm_df[(open_bpm_df['dueDate']-today)/np.timedelta64(1, 'D')==2.0]['dueDate'].count()
#(open_bpm_df['dueDate']-today)
(open_bpm_df['dueDate']-today)/np.timedelta64(1, 'D')


# In[ ]:


today_val=open_bpm_df[(pd.to_datetime(open_bpm_df['dueDate'])-pd.to_datetime("now"))//np.timedelta64(1, 'D')==0]['dueDate'].count()


# In[ ]:


today_val


# In[ ]:




