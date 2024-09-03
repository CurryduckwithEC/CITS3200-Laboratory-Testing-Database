# See official docs at https://dash.plotly.com
# pip install dash pandas

from dash import Dash, dcc, html, Input, Output
import plotly.express as px

import pandas as pd

import sys
import signal

# Define the exit behaviour of Dash
# Normally SIGINT would leave an orphaned Flask process running
def termination_handler(sig, frame):
    print("SIGINT received: terminating Flask server.")
    sys.exit(0)

signal.signal(signal.SIGINT, termination_handler)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        df['year'].min(),
        df['year'].max(),
        step=None,
        value=df['year'].min(),
        marks={str(year): str(year) for year in df['year'].unique()},
        id='year-slider'
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = df[df.year == selected_year]

    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55)

    return fig

port = "18019"


if len(sys.argv) > 1:
    port = sys.argv[1]

app.run_server(port=port, debug=True)