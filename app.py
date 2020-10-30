# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# Autor: Andres Felipe Acevedo

import dash
import dash_core_components as dcc
import dash_html_components as html
from components import Components
from dash.dependencies import Input, Output
import requests
import pandas as pd
import json
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import datetime
    
#Utils
def filterDict(dictionary, multi_drop):
    d = {}
    d['Country'] = dcc.Link(
        children=html.Div([
            
            html.Img(src=dictionary['countryInfo']['flag'],style={'object-fit':'contain','width':'5%','padding':'10px'}),
            str(dictionary['country']),
        
        ],className="row"),
    href=f"/{dictionary['countryInfo']['iso2']}")

    for x in multi_drop:
        d[x.title()] = dictionary[x]
    return d



#Backend

BASE_URL = 'https://disease.sh/v3/covid-19/'
ENTRY_HISTORICAL_ALL = "historical/all"
HISTORICAL="historical"
ENTRY_COUNTRYS='countries'
today=datetime.date.today()


cps = Components()


app = dash.Dash(__name__,
    external_stylesheets=["https://fonts.googleapis.com/css2?family=Montserrat:wght@100;300;400&display=swap",
    dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

Header = dcc.Link(
            className="header",
            children=[
                html.Img(src=app.get_asset_url('covid.png'),
                    style={'width': '10%',
                    'padding-right': '10px',
                    'object-fit': 'contain',
                    'max-width':'70px'}),
                html.H3("Covid-Tracker")],
            href="/")



home = html.Div([
    Header,
    
    html.Div([
    html.Div([
        html.H4(f"Covid 19 Tracker At {today.strftime('%d, %b %Y')}",id="title",className="title"),
        cps.CountryDrop,],
        className="country_select"),
    cps.InputDays,
    cps.InputVariable,
    html.Div(
        children=[
            cps.Graph,
            html.Div([html.H5("Choose data"),cps.MultiDrop, cps.OrderDrop], className="table_filters"),
            html.H5("Live Cases By Country"),
            cps.Table],
        className="data_container")
    
    ],className="app_body")
    
],className="app")



country = html.Div([
    Header,
    html.Div([
    html.Div([
        html.Div(id="title_country",className="title")],
        className="country_select"),
    cps.InputDays,
    cps.InputVariable,
    html.Div(
        children=[
            cps.Graph,
            html.Div([html.H5("Choose data"),cps.MultiDrop, cps.OrderDrop], className="table_filters"),
            html.H5("Live Cases By Country"),
            cps.Table],
        className="data_container")
    
    ],className="app_body")
    
],className="app")




#Callbacks

# Update the index
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname=="/None":
        return home
    else:
        return country
    # You could also return a 404 "URL not found" page here






#Update Drop Countries
@app.callback(
    Output("country_drop", 'options'),
    [Input("title",'children')]
)
def update_countries(x):
    r = requests.get(f"{BASE_URL}{ENTRY_COUNTRYS}")
    res = r.json()
    ops = [{'label':x['country'], 'value':x['countryInfo']['iso2']}  for x in res if x['countryInfo']['iso2']!= None]
    return ops


#Update Url

@app.callback(
    Output('url', 'pathname'),
    [Input("country_drop",'value')]
)

def update_url(country):
    return f"/{country}"


#UpdateTitle
@app.callback(
    Output("title_country", 'children'),
    [Input("url",'pathname')]
)
def update_title(pathname):
    return [html.Img(src=f"https://disease.sh/assets/img/flags{pathname.lower()}.png",style={'width':'17%','max-width':'80px','padding-right':'10px','object-fit':'contain'}),
            html.H5(f"Covid 19 Tracker At {today.strftime('%d, %b %Y')}",className="title")]

#UpdateGraph
@app.callback(
    Output(component_id='graph_cases', component_property='figure'),
    [Input(component_id='input_days', component_property='value'),
    Input("input_variable", 'value'),
    Input('url', 'pathname')]
)
def update_graph(input_days, input_variable,pathname):
    
    color_dict = {'cases': '#1967d2', 'deaths': '#cc1034', 'recovered': '#90ee90'}

    if pathname=="/" or pathname=="/None":
        r = requests.get(f"{BASE_URL}{ENTRY_HISTORICAL_ALL}?lastdays={input_days}")
        res = r.json()
        df = pd.DataFrame(res)
        title=f"New {input_variable.title()} In Last {input_days} Days (Worldwide)"
    else:
        r = requests.get(f"{BASE_URL}{HISTORICAL}{pathname}?lastdays={input_days}")
        res = r.json()
        df = pd.DataFrame(res['timeline'])
        title=f"New {input_variable.title()} In Last {input_days} Days ({res['country']})"
    df[f'New {input_variable}'] = df[f"{input_variable}"].diff()
    df=df.dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[f'New {input_variable}'], fill='tozeroy',line_color=color_dict[input_variable])) # fill down to xaxis
    fig.layout={'title':title,'paper_bgcolor':'rgba(0,0,0,0)',
            'plot_bgcolor':'rgba(0,0,0,0)'}
    return fig


#Update Sort Dropdown

@app.callback(
    Output("order_drop", 'options'),
    Input("multi_drop",'value')
)
def update_sort_drop(multi_drop):
    return [{'label':x.title(), 'value':x} for x in multi_drop]


#UpdateTable
@app.callback(
    Output(component_id='table', component_property='children'),
    [Input("multi_drop", 'value'),
    Input("order_drop", 'value'),
    Input("url",'pathname')]
)
def update_table(multi_drop, order_drop, pathname):
    if pathname=="/" or pathname=="/None":
        r = requests.get(f"{BASE_URL}{ENTRY_COUNTRYS}")
        res = r.json()
        data=[filterDict(dictionary,multi_drop) for dictionary in res]
        df = pd.DataFrame(data)
    else:
        r = requests.get(f"{BASE_URL}{ENTRY_COUNTRYS}{pathname}")
        res = r.json()
        data=[filterDict(res,multi_drop)]
        df = pd.DataFrame(data)
    if order_drop==None:
        df = df.sort_values(by=multi_drop[0].title(), ascending=False)
    else:
        try:
            df = df.sort_values(by=order_drop.title(), ascending=False)
        except KeyError:
            df = df.sort_values(by=multi_drop[0].title(), ascending=False)
    return dbc.Table.from_dataframe(df,
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,)











if __name__ == '__main__':
    app.run_server(debug=False)