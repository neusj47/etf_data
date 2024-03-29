# 국내, 해외 기초자산 ETF 기간수익률 차트
# 1. URL 데이터를 Json 형식으로 읽어온다.
# 2. 크롤링한 데이터 속에서 3M기간 수익률 / 당일 거래금액 차트를 만든다.
# 3. 국내, 해외 기초자산별 Sheet을 만든다.

import pandas as pd
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
from bs4 import BeautifulSoup


url_kor = "https://finance.naver.com/api/sise/etfItemList.nhn?etfType=0&targetColumn=market_sum&sortOrder=desc"
url_for = "https://finance.naver.com/api/sise/etfItemList.nhn?etfType=4&targetColumn=market_sum&sortOrder=desc"
etf_kor_data = pd.DataFrame(requests.get(url_kor).json()["result"]['etfItemList'])
etf_for_data = pd.DataFrame(requests.get(url_for).json()["result"]['etfItemList'])

kor_amt_top = etf_kor_data.sort_values('quant').tail(30)
kor_rtn_top = etf_kor_data.sort_values('changeRate').tail(30)
kor_amt_top = kor_amt_top.reset_index(drop=False)
kor_rtn_top = kor_rtn_top.reset_index(drop=False)

for_amt_top = etf_for_data.sort_values('quant').tail(30)
for_rtn_top = etf_for_data.sort_values('changeRate').tail(30)
for_amt_top = for_amt_top.reset_index(drop=False)
for_rtn_top = for_rtn_top.reset_index(drop=False)

kor_fig_amt = px.scatter(kor_amt_top, x='amonut', y='threeMonthEarnRate', color = 'itemname', custom_data=['quant'])
kor_rtn = px.scatter(kor_amt_top, x='amonut', y='threeMonthEarnRate', color = 'itemname', custom_data=['changeRate'])
for_fig_amt = px.scatter(for_amt_top, x='amonut', y='threeMonthEarnRate', color = 'itemname', custom_data=['quant'])
for_rtn = px.scatter(for_amt_top, x='amonut', y='threeMonthEarnRate', color = 'itemname', custom_data=['changeRate'])


kor_rtn_top = kor_rtn_top[['itemname', 'changeRate', 'threeMonthEarnRate', 'quant', 'amonut','marketSum']]
kor_rtn_top.columns = ['ETF명', '일간수익률', '3개월수익률','거래량','거래금액','시가총액']
for_rtn_top = for_rtn_top[['itemname', 'changeRate', 'threeMonthEarnRate', 'quant', 'amonut','marketSum']]
for_rtn_top.columns = ['ETF명', '일간수익률', '3개월수익률','거래량','거래금액','시가총액']


def crawl(url):
    data = requests.get(url)
    print(data)
    return data.content

def getStockInfo(tr):
    tds = tr.findAll("td")
    rank = tds[0].text
    aTag = tds[1].find("a")
    href = aTag["href"]
    name = aTag.text
    Price = tds[2].text
    Volume = tds[9].text
    PER = tds[10].text
    ROE = tds[11].text
    return {"rank":rank, "name":name, "href":href, "code":href[20:],
            "nowPrice":Price, "Volume":Volume, "PER":PER, "ROE":ROE}

def parse(pageString):
    bsObj = BeautifulSoup(pageString, "html.parser")
    box_type_l = bsObj.find("div", {"class":"box_type_l"})
    type_2 = box_type_l.find("table",{"class":"type_2"})
    tbody = type_2.find("tbody")
    trs = tbody.findAll("tr")
    stockInfos = []
    for tr in trs:
        try:
            stockInfo = getStockInfo(tr)
            stockInfos.append(stockInfo)
        except Exception as e:
            print("error")
            pass
    return stockInfos

def getSiseMarketSum(sosok, page):
    url = "https://finance.naver.com/sise/sise_market_sum.nhn?sosok={}&page={}".format(sosok, page)
    pageString = crawl(url)
    list = parse(pageString)
    return list

result = []

for page in range(1, 3 + 1):
    list = getSiseMarketSum(0, page) #0 코스피 1코스닥
    result += list
print(result)

result_dq = []
for page in range(1, 3 + 1):
    list = getSiseMarketSum(1, page) #0 코스피 1코스닥
    result_dq += list
print(result_dq)

secu_data = pd.DataFrame(result)
secu_data_dq = pd.DataFrame(result_dq)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "17rem",
    "margin-right": "1rem",
    "padding": "2rem 1rem",
}


sidebar = html.Div(
    [
        html.H2("ETF Dash", className="display-4"),
        html.Hr(),
        html.P(
            "ETF Monitoring", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("KOREA", href="/KOREA", active="exact"),
                dbc.NavLink("INTERNATIONAL", href="/INTERNATIONAL", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/KOREA":
        return html.Div([
    dcc.Tabs([
        dcc.Tab(label = "3M 수익률/거래량", children = [
            html.H3("국내 ETF 차트"),
            dcc.Graph(
                id = 'my-graph',
                style={'height': 600},
                figure = kor_rtn
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
                    for i in kor_rtn_top.columns
                ],
                data=kor_rtn_top.to_dict("records"),  # the contents of the table
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
                })
            ]),
            dcc.Tab(label="KOSPI", children=[
                html.H3("종목 주가 정보"),
                dash_table.DataTable(
                    id="datatable-interactivity_secu",
                    columns=[
                        {
                            "name": i,
                            "id": i,
                            "deletable": False,
                            "selectable": True,
                            "hideable": False,
                        }
                        for i in secu_data.columns
                    ],
                    data=secu_data.to_dict("records"),  # the contents of the table
                    sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                    sort_mode="single",  # sort across 'multi' or 'single' columns
                    page_action="native",  # all data is passed to the table up-front or not ('none')
                    page_size=20,  # number of rows visible per page
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
                    })
                ]),
        dcc.Tab(label="KOSDAQ", children=[
            html.H3("종목 주가 정보"),
            dash_table.DataTable(
                id="datatable-interactivity_secu",
                columns=[
                    {
                        "name": i,
                        "id": i,
                        "deletable": False,
                        "selectable": True,
                        "hideable": False,
                    }
                    for i in secu_data_dq.columns
                ],
                data=secu_data_dq.to_dict("records"),  # the contents of the table
                sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                sort_mode="single",  # sort across 'multi' or 'single' columns
                page_action="native",  # all data is passed to the table up-front or not ('none')
                page_size=20,  # number of rows visible per page
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
                })
            ])
        ])
        ])
    elif pathname == "/INTERNATIONAL":
        return html.Div([
        html.H3("해외 ETF 3M 수익률/거래량 차트"),
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
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


#
# app.layout = html.Div([
#     html.H3("ETF별 3M 수익률/거래량 차트 "),
#     dcc.Graph(
#         id = 'my-graph',
#         style={'height': 600},
#         figure = for_rtn
#     ),
#     dash_table.DataTable(
#         id="datatable-interactivity",
#         columns=[
#             {
#                 "name": i,
#                 "id": i,
#                 "deletable": False,
#                 "selectable": True,
#                 "hideable": False,
#             }
#             for i in for_rtn_top.columns
#         ],
#         data=for_rtn_top.to_dict("records"),  # the contents of the table
#         sort_action="native",  # enables data to be sorted per-column by user or not ('none')
#         sort_mode="single",  # sort across 'multi' or 'single' columns
#         page_action="native",  # all data is passed to the table up-front or not ('none')
#         page_size=15,  # number of rows visible per page
#         style_cell={  # ensure adequate header width when text is shorter than cell's text
#             "minWidth": 95,
#             "maxWidth": 200,
#             "width": 95,
#         },
#         # style_cell_conditional={
#         #     'textAlign': 'left'
#         # },
#         style_data={  # overflow cells' content into multiple lines
#             "whiteSpace": "normal",
#             "height": "auto",
#         },
#         style_data_conditional=[
#             {
#                 'if': {'row_index': 'odd'},
#                 'backgroundColor': 'rgb(248, 248, 248)'
#             }
#         ],
#         style_header={
#             'backgroundColor': 'rgb(230, 230, 230)',
#             'fontWeight': 'bold'
#         }
#     )
# ])

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)


