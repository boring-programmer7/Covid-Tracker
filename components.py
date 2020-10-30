import dash_core_components as dcc
import dash_html_components as html


class Components():
    def __init__(self):
        
        self.CountryDrop=dcc.Dropdown(id="country_drop",placeholder="Worldwide")
        self.InputDays=dcc.Dropdown(
                id='input_days',
                options=[{'label': f"{i} days", 'value': i} for i in [7,15,30]],
                value=7)
        self.InputVariable=dcc.Dropdown(
                id='input_variable',
                options=[{'label': i.title(), 'value': i} for i in ['cases','deaths','recovered']],
                value='cases')
        self.Graph = dcc.Loading(children=dcc.Graph(id="graph_cases",className="graph",config=dict(displayModeBar=False)), type='circle')
        self.Table = dcc.Loading(children=html.Div(className="tableDash", id="table"), type="circle")
        self.MultiDrop = dcc.Dropdown(
            id="multi_drop",
            options=[
                {'label':x.title() , 'value': x}
            for x in ['cases','todayCases','deaths','todayDeaths','recovered','todayRecovered']
            ],
            value=['cases','deaths'],
            multi=True)
        self.OrderDrop = dcc.Dropdown(id="order_drop",
        options=[{'label':x.title(), 'value':x} for x in self.MultiDrop.value],
        placeholder="Sort by")
