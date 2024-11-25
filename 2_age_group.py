import dash
from dash import dcc, callback, Input, Output

from dash import html

import pandas as pd
import numpy as np
import datetime
import plotly.express as px
from config import connect
from scripts.retrieve_queries import gharane_lastname, age_group_sql

colors = {"background": "#111111", "text": "#7FDBFF"}

dash.register_page(__name__, name="Ages", path="/age_group")

conn = connect()
cur = conn.cursor()

radio_button_selection = ["gharane", "lastName"]

def member_age(source_data):
    source_data["birthDate"] = pd.to_datetime(source_data["birthDate"], errors="coerce")
    source_data["deathDate"] = pd.to_datetime(source_data["deathDate"], errors="coerce")
    df = source_data[source_data["livingStatus"] == "Living"]

    new_df = df[(df.birthDate.notnull()) & (df.deathDate.isnull())]

    new_df = new_df[["id", "gharane", "lastName", "birthDate", "deathDate"]]
    new_df["age"] = datetime.datetime.now().year - new_df["birthDate"].dt.year
    new_df["age"] -= (
        (datetime.datetime.now().month * 32 + datetime.datetime.now().day)
        - (new_df["birthDate"].dt.month * 32 + new_df["birthDate"].dt.day)
    ).apply(lambda x: 1 if x < 0 else 0)
    new_df["age_groups"] = pd.cut(
        new_df.age,
        [0, 15, 30, 45, 60, 75, 90, 100, 200],
        labels=["0-15", "16-30", "31-45", "46-60",
                "61-75", "76-90", "91-100", "100+"],
    )
    df2 = new_df.groupby("age_groups")["age"].count().reset_index()
    fig = px.bar(df2, x="age_groups", y="age", text="age")
    fig.update_traces(textposition="outside")
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        xaxis={"showgrid": False},
        yaxis={"showgrid": False},
    )

    return fig


layout = html.Div(
    [dcc.Interval(
        id='update-interval-1',
        interval=86400 * 1000, # in milliseconds
        n_intervals=0
    ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "Age Group Distribution for Living members",
                                    style={
                                        "margin-bottom": "0px",
                                        "textAlign": "center",
                                        "color": colors["text"],
                                    },
                                ),
                            ]
                        )
                    ]
                )
            ]
        ),
        html.Div(
            children=[
                html.Label("Select Gharane / Surname"),
                html.Br(),
                html.Br(),
                dcc.RadioItems(
                    # radio_button_selection,
                    options = [
                        {'label' : 'Gharane' , 'value': 'gharane'},
                        {'label' : 'Surname' , 'value' : 'lastName'}
                    ],
                    value = "gharane",
                    id="gharane_selection",
                    # inline=True,
                ),
                html.Br(),
                # html.Br(),
                html.Label("Select Options"),
            ],
            style={
                "backgroundColor": colors["background"],
                "margin-bottom": "0px",
                "margin-left": "5px",
                "textAlign": "left",
                "color": colors["text"],
                "fontSize": 20,
            },
        ),
        html.Div(
            id="dropdown-div",
            children=[
                html.Br(),
                dcc.Dropdown(
                    id="surname_dropdown",
                    clearable=True,
                    style={
                        "display": True,
                        "backgroundColor": colors["background"],
                    },
                    placeholder="Select Options",
                    className="drop-zone-dropdown",
                ),
                html.Br(),
                html.Br(),
            ],
            style={
                "width": "25%",
                "margin-left": "5px",
                "display": "inline-block",
                "backgroundColor": colors["background"],
            },
        ),
        dcc.Graph(
            id="birth-periods-graph",
        ),
    ]
)


@callback(
    Output("surname_dropdown", "options"),
    Output("surname_dropdown", "value"),
    Input('update-interval-1', 'n_intervals'),
    Input("gharane_selection", "value"),
)
def update_radio_button_selection(n_intervals, gharane_selection):
    cur.execute(gharane_lastname)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['gharane','lastName'])

    if gharane_selection == "gharane":
        options = [
            {"label": i, "value": i}
            for i in np.append(["All"], main_df["gharane"].unique())
        ]
        value = "All"
    else:
        options = [
            {"label": i, "value": i}
            for i in np.append(["All"], main_df["lastName"].unique())
        ]
        value = "All"
    return options, value

@callback(
    Output(component_id="birth-periods-graph", component_property="figure"),
    Input("gharane_selection", "value"),
    Input(component_id="surname_dropdown", component_property="value"),
)
def age_calc(radio_selection_value, value):
    cur.execute(age_group_sql)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['id','gharane','lastName','birthDate','deathDate', 'livingStatus'])

    if value != "All":
        main_df = main_df[main_df[radio_selection_value] == value]
    fig = member_age(main_df)

    return fig