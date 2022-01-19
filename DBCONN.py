# %%
import pyodbc
import pandas as pd
pd.options.mode.chained_assignment=None
import numpy as np

def mydbconn(dbname='',userid='',passwd='',server=''):
	cnx = pyodbc.connect(
    server="hide.czsauxqf1c8t.ap-southeast-1.rds.amazonaws.com",
    #database="PDS_SAP_CLONE",
    database=dbname,
    user=userid,
    tds_version='7.4',
    password=passwd,
    port=1433,
    driver='FreeTDS')
	return cnx

def runsql(stmt,cursor):
	result = pd.read_sql_query(stmt,cursor)
	pd.set_option('display.float_format', lambda x: '%.5f' % x)
	return result
#cnx=mydbconn("PDS_SAP_clone",'DbView','welcome@2020')
#result=runsql('select * from dbo.tb_po_details',cnx)
#print(result)