from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State

import plotly.express as px
import pandas as pd
import csv
import random

app = Dash(__name__)

with open("Police_Fatalities.csv", 'r') as file:
    reader = csv.DictReader(file)
    next(reader)
    data_pd = pd.DataFrame(reader)

min_zakres = random.randint(0, 12400)
max_zakres = random.randint(min_zakres, 12400)

app.layout = html.Div(children=[
    html.H3(children='''Wykres przedstawiające liczbę ofiar policji dla poszczególnych stanów USA 
                        z podziałem na płeć'''),

    html.Button('Przeładuj dane', id='przycisk', n_clicks=0, style={'float': 'right'}),

    html.Br(),

    html.Div(
        dcc.Checklist(
            id="plec",
            options=['Male', 'Female'],
            value=['Male', 'Female']
        ),
    ),

    dcc.Graph(
        id='wykresik'
        # figure=fig
    ),

    dcc.Graph(
        id='podzial_plec',
        figure=px.pie(values=[0, 0], names=["Male", "Female"],
                      color_discrete_map={'Male': 'blue',
                                          'Female': 'pink'},
                      title="Podział ofiar policji ze względu na płeć w stanie {nie wybrano}")
    )
])


@app.callback(
    Output(component_id='wykresik', component_property='figure'),
    Input(component_id='przycisk', component_property='n_clicks'),
    Input(component_id='plec', component_property='value')
)
def update_graph(n_clicks, plec):
    global min_zakres, max_zakres

    print(ctx.triggered_id)

    if ctx.triggered_id == 'przycisk':
        min_zakres = random.randint(0, 12000)
        max_zakres = random.randint(min_zakres + 1, 12400)

    df = data_pd[min_zakres:max_zakres]
    states = data_pd["State"].unique()
    states = pd.DataFrame(states, columns=["State"])

    df = df[df["Gender"].isin(plec)]
    df = df[["UID", "State"]]
    df = df.groupby(["State"])["UID"].count().reset_index()
    df = df[["State", "UID"]]

    df = pd.merge(states, df, how="left", on="State")
    df["UID"] = df["UID"].fillna(int(0))

    print(df)
    min_rang_col = 0
    max_rang_col = 5
    if not df.empty:
        if max(df["UID"] > 5):
            max_rang_col = max(df["UID"])

    fig = px.choropleth(
        df,
        locations=df["State"],
        locationmode="USA-states",
        color="UID",
        color_continuous_scale="Reds",
        # hover_name="UID",
        scope="usa",
        range_color=[min_rang_col, max_rang_col],
        title="Liczba ofiar policjantów w zależności od stanu USA",
    )

    return (fig)


@app.callback(
    Output(component_id="podzial_plec", component_property="figure"),
    Input(component_id='wykresik', component_property='clickData')
)
def update_graph2(clickData):
    global min_zakres, max_zakres

    df = data_pd[min_zakres:max_zakres]

    location = clickData["points"][0]["location"]

    df = df[df["State"] == location]
    df = df.groupby("Gender")["UID"].count().reset_index()
    df = pd.DataFrame(df)

    genders = ['Male', 'Female']
    genders = pd.DataFrame(genders, columns=["Gender"])
    genders = pd.merge(genders, df, how="left", on="Gender")

    tit = "Podział ofiar policji ze względu na płeć w stanie '" + str(location) + "'"

    fig = px.pie(genders, values='UID', names='Gender',
                 color_discrete_map={'Male': 'blue',
                                     'Female': 'pink'},
                 title=tit)

    return (fig)


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8080')