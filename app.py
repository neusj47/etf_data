import pandas as pd
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import date


url_for = "https://finance.naver.com/api/sise/etfItemList.nhn?etfType=4&targetColumn=market_sum&sortOrder=desc"

etf_for_data = pd.DataFrame(requests.get(url_for).json()["result"]['etfItemList'])

for_amt_top = etf_for_data.sort_values('quant').tail(30)
for_rtn_top = etf_for_data.sort_values('changeRate').tail(30)
for_amt_top = for_amt_top.reset_index(drop=False)
for_rtn_top = for_rtn_top.reset_index(drop=False)


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#
#
# app.layout = html.Div([
#     html.H3("기간별 monte carlo simuation"),
#     dcc.Graph(
#         style={'height': 600},
#         id='my-graph'
#     ),
#     dcc.Graph(id='my-graph2', figure={}, clickData=None, hoverData=None)
# ])