import dash
from dash import dash_table, dcc, callback, Input, Output

from dash import html

import pandas as pd
import numpy as np
import psycopg2
import plotly.express as px
from config import connect
from scripts.retrieve_queries import gharane_lastname, country_state_sql

colors = {"background": "#111111", "text": "#7FDBFF"}

dash.register_page(__name__, name="Education", path="/education")

conn = connect()
cur = conn.cursor()

radio_button_selection = ["gharane", "lastName"]

tab_style = {
    "background": "#323130",
    # 'text-transform': 'uppercase',
    'color': '#7FDBFF',
    'border': 'grey',
    'font-size': '20px',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding':'6px'
}

tab_selected_style = {
    "background": "grey",
    # 'text-transform': 'uppercase',
    'color': '#7FDBFF',
    'font-size': '20px',
    'font-weight': 600,
    'align-items': 'center',
    'justify-content': 'center',
    'border-radius': '4px',
    'padding':'6px'
}
# radio_button_selection = ["gharane", "lastName"]
radio_button_selection = {
    'Gharane' : 'gharane',
    'Surname' : 'lastName'
}


layout = html.Div(
    [   dcc.Interval(
        id='update-interval-1',
        interval=86400 * 1000, # in milliseconds
        n_intervals=0
        ),
        dcc.Tabs(id = 'tabs', value = 'education_analysis', children = [
            dcc.Tab(label = 'Most Prevalent Categories (सर्वात प्रचलित श्रेणी)', value = 'prevalent_categories' , style=tab_style, selected_style=tab_selected_style, 
                children = [

                ]
                    )
                                                                        ]
                )
    ]
                )
                
