# %%
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import io
from flask import send_file
import dash_table
app = dash.Dash()
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from plotly import graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import date
from datetime import timedelta
from dash.dash import no_update
from dash.exceptions import PreventUpdate

#for temp sake, report2 df is written to csv and then being read here. This is useful for debugging and testing which 
#avoids re running all the above code.

report2=pd.read_csv('/Users/nagarajugooty/Downloads/po_data.csv',low_memory=False)

#convert PO Date from object to datetime type.
report2['PO Date']=pd.to_datetime(report2['PO Date'])
print('Hello here')

#trying out a function in update_figure
def get_data(vendor_type,postatus,supplier,start_dt):
    return report2


def set_po_status(base):
    if base == "GARMENT":
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Vendor Type']=='GARMENT']['Status'].unique()),
        })
    elif base== "FABRIC":
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Vendor Type']=='FABRIC']['Status'].unique()),
        })
    else:
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Vendor Type']=='TRIMS']['Status'].unique()),
        })

def set_supplier(base):
    if base == "New":
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Status']=='New']['Supplier'].unique()),
        })
    elif base== "Accepted":
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Status']=='Accepted']['Supplier'].unique()),
        })
    elif base== "Closed":
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Status']=='Closed']['Supplier'].unique()),
        })
    else:
        return pd.DataFrame(data={
            "produit": sorted(report2[report2['Status']=='Rejected']['Supplier'].unique()),
        })
    
app = dash.Dash(__name__)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

res_ad = False

# Website choice
site = "GARMENT"

site_name = {"GARMENT": "GARMENT",
             "FABRIC": "FABRIC",
             "TRIMS": "TRIMS"
             }

zdates= {'Monthly':'Monthly',
         'Quarterly': 'Quarterly',
         'Semi Annually': 'Semi Annually',
         'Annually': 'Annually'}



df = set_po_status(site)

# Dropdown menu for vendor_type :
opts_site = [{'label': str(site_name[i]), 'value': str(i)} for i in site_name.keys()]

# Dropdown menu for Dates :
opts_zdate = [{'label': str(zdates[i]), 'value': str(i)} for i in zdates.keys()]

datatable=dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in report2.columns],
    #data=report2.to_dict("rows"),
)

fig = go.Figure()
fig.add_trace(go.Table(
    header=dict(values=list(report2.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[report2],
               fill_color='lavender',
               align='left')
))

graph = dcc.Graph(id='potable', figure=fig, style={"height": "100vh", "width": "95vw"})
print('before app.layout')
app.layout = html.Div([
    html.Div([
        html.H1(children="Purchase Order Dashboard",
                id='heading',
                style={
                    'textAlign': 'center',
                }),
    ]),
    html.P([
        html.Label("Vendor Type"),
        dcc.Dropdown(
            id='vendor_type',
            options=opts_site,
            value='FABRIC')
    ],
        style={
            'textAlign': 'center',
            'width': '200px',
            'fontSize': '20px',
            'display': 'inline-block'}
    ),
    html.P([
        html.Label("PO Status"),
        dcc.Dropdown(id='postatus')
    ],
        style={
            'textAlign': 'center',
            'width': '200px',
            'fontSize': '20px',
            'padding-left': '100px',
            'display': 'inline-block'}
    ),
    html.P([
        html.Label("Supplier"),
        dcc.Dropdown(id='supplier')
    ],
        style={
            'textAlign': 'center',
            'width': '400px',
            'fontSize': '20px',
            'padding-left': '10px',
            'display': 'inline-block'}
    ),
    html.P([
        html.Label("Date"),
        dcc.Dropdown(id='zdate',
            options=opts_zdate,
            value='Date')
    ],
        style={
            'textAlign': 'center',
            'width': '200px',
            'fontSize': '20px',
            'padding-left': '100px',
            'display': 'inline-block'}
    ),
    html.Div([
        html.H1(children="Purchase Order sub dashboard",
                style={
                    'textAlign': 'center',
                }),
    ]),
    #,
    graph
    
    ])
print('hello before callback')
@app.callback(output=[
                      Output('postatus', 'options'),
                      Output('postatus', 'value')],
              inputs=[Input('vendor_type', 'value')])
def update_postatus_options(vendor_type):
        df = set_po_status(vendor_type)
        return [{'label': str(i), 'value': str(i)} for i in df.produit.unique()], df.produit.unique()[0]

@app.callback(output=[Output('supplier', 'options'),
                      Output('supplier', 'value')],
              inputs=[Input('postatus', 'value')])
def update_supplier_options(postatus):
        df = set_supplier(postatus)
        return [{'label': str(i), 'value': str(i)} for i in df.produit.unique()], df.produit.unique()[0]
'''
@app.callback(output=Output('heading','value'),
              inputs=[Input('zdate','value')],
              )
def update_zdate(zdate):
        if (not zdate or zdate=='Monthly'):
            return start
        elif zdate=='Quarterly':
            start=end - timedelta(days=90)
        elif zdate=='Semi Annually':
            start=end - timedelta(days=180)
        else:
            start=end - timedelta(days=365)
        return update_figure(vendor_type, postatus, supplier, start,4)
'''
@app.callback(output=Output('potable', 'figure'),
              inputs=[Input('vendor_type', 'value'),
                     Input('postatus','value'),
                     Input('supplier','value'),
                     Input('zdate','value')]
             )

def update_figure(vendor_type, postatus, supplier, zdate):

        end = date.today()
        start = end - timedelta(days=30)
        if not zdate:
            return start
        elif zdate=='Quarterly':
            start=end - timedelta(days=90)
        elif zdate=='Semi Annually':
            start=end - timedelta(days=180)
        else:
            start=end - timedelta(days=365)
        
#    start_dt = pd.to_datetime(start_dt).date()
#    end_dt = date.today()

        dff=report2.copy()
        trace = go.Table(
        header=dict(values=list(dff.columns),
                fill_color='paleturquoise',
                align='left'),
            #cells=dict(values=[report2[i] for i in report2.columns],
            cells=dict(values=[dff['PO'],dff['Status'],dff['Vendor Type']],
                        #cells=dict(values=[dff[i] for i in dff.columns],
               fill_color='lavender',
               align='left')
)
        return fig.add_trace(trace)
        #return data.to_dict('rows')
    #return go.Figure(data=trace)
    #df = report2[[vendor_type,postatus,supplier]]
    

app.config['suppress_callback_exceptions'] = True

app.run_server()