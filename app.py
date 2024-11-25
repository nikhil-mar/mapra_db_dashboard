from dash import Dash, html, dcc
import dash
# from datetime import datetime
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CERULEAN])

sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page['name'], className='ms-2'),
            ],
            href=page["path"],
            active="exact"
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className='bg-dark',
)

# app.layout = html.Div(
app.layout = dbc.Container(
    [
        html.Br(),
        
    dbc.Row(
        [
            dbc.Col(
                [
                    sidebar
                ],
                xs=4, sm=4, lg=2, xl=2, xxl=2
            ),

            dbc.Col(
                [
                    dash.page_container
                ], xs=8, sm=8, lg=10, xl=10, xxl=10
            )
        ]
    )
    ],fluid=True
)


if __name__ == "__main__":

    app.run_server()
