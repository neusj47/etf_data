import pandas as pd
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table
from dash.dependencies import Input, Output, State

url_for = "https://finance.naver.com/api/sise/etfItemList.nhn?etfType=4&targetColumn=market_sum&sortOrder=desc"

etf_for_data = pd.DataFrame(requests.get(url_for).json()["result"]['etfItemList'])

for_amt_top = etf_for_data.sort_values('quant').tail(30)
for_rtn_top = etf_for_data.sort_values('changeRate').tail(30)
for_amt_top = for_amt_top.reset_index(drop=False)
for_rtn_top = for_rtn_top.reset_index(drop=False)
fig_amt = px.scatter(for_amt_top, x='amonut', y='threeMonthEarnRate', color = 'itemname', custom_data=['quant'])
for_rtn = px.scatter(for_amt_top, x='amonut', y='threeMonthEarnRate', color = 'itemname', custom_data=['changeRate'])

for_rtn_top = for_rtn_top[['itemname', 'changeRate', 'threeMonthEarnRate', 'quant', 'amonut','marketSum']]
for_rtn_top.columns = ['ETF명', '일간수익률', '3개월수익률','거래량','거래금액','시가총액']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.H3("ETF별 3M 수익률/거래량 차트 "),
    dcc.Graph(
        id = 'my-graph',
        style={'height': 600},
        figure = for_rtn
    ),
    dash_table.DataTable(
        id="datatable-interactivity",
        columns=[
            {
                "name": i,
                "id": i,
                "deletable": False,
                "selectable": True,
                "hideable": False,
            }
            for i in for_rtn_top.columns
        ],
        data=for_rtn_top.to_dict("records"),  # the contents of the table
        sort_action="native",  # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",  # sort across 'multi' or 'single' columns
        page_action="native",  # all data is passed to the table up-front or not ('none')
        page_size=15,  # number of rows visible per page
        style_cell={  # ensure adequate header width when text is shorter than cell's text
            "minWidth": 95,
            "maxWidth": 200,
            "width": 95,
        },
        # style_cell_conditional={
        #     'textAlign': 'left'
        # },
        style_data={  # overflow cells' content into multiple lines
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8060)


