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

dash.register_page(__name__, name="Places", path="/places")

conn = connect()
cur = conn.cursor()

# radio_button_selection = ["gharane", "lastName"]
radio_button_selection = {
    'Gharane' : 'gharane',
    'Surname' : 'lastName'
}

def header_value(header_data, value, radio_selection_value):
    if value == 'All':
        # return [f"{value}"]
        return "All (सर्व)"
    else:
        if radio_selection_value == 'gharane':
            gharane_header = header_data[header_data['gharane'] == value]
            gharane_header = gharane_header['gharane'] + ' (' + gharane_header['gharane_m'] + ')'
            gharane_headerheader = gharane_header.tolist()
            
            return [f"{gharane_headerheader[0]}"]
        else:
            surname_header = header_data[header_data['lastName'] == value]
            surname_header = surname_header['lastName'] + ' (' + surname_header['last_name_m'] + ')'
            surname_header = surname_header.tolist()
            
            return [f"{surname_header[0]}"]


def states_datatable(value, source_data):
    df = source_data[source_data["provinceOrState"] != ""]
    
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)
    df = df[df['country'] == 'India']

    df['state_combined'] = df['provinceOrState'] + ' (' + df['provinceOrState_m'] + ')'
    

    if value == "All":
        df = df[["id", "state_combined"]]
        df = df.groupby(["state_combined"])["id"].count().reset_index()
    else:
        df = df[["id", "state_combined"]]
        df = df.groupby(["state_combined"])["id"].count().reset_index()

    df = df.rename(columns={"state_combined" : "State (राज्य)","id": "COUNTS"})
    df = df.sort_values(["COUNTS"], ascending=[False])
    df = df.head(10)
    ret_df = df.to_dict("records")
    
    return ret_df

def country_datatable(value, source_data):
    df = source_data[source_data["country"] != ""]
    # df["country"] = df["country"].str.strip()
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)

    df['country_combined'] = df['country'] + ' (' + df['country_m'] + ')'
    print(df.dtypes)
    

    if value == "All":
        df = df[["id", "country_combined"]]
        df = df.groupby(["country_combined"])["id"].count().reset_index()
    else:
        df = df[["id", "country_combined"]]
        df = df.groupby(["country_combined"])["id"].count().reset_index()

    df = df.rename(columns={"country_combined":"Country (देश)","id": "COUNTS"})
    df = df.sort_values(["COUNTS"], ascending=[False])
    df = df.head(10)
    ret_df = df.to_dict("records")
    
    return ret_df

layout = html.Div(
    [
        dcc.Interval(
        id='update-interval-2',
        interval=86400 * 1000, # in milliseconds
        n_intervals=0
    ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [html.Br(),
                                html.H1(
                                    "Top 10 places- Living Persons (सर्वाधिक लोकप्रिय 10 निवासस्थाने)",
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
                html.Br(),
                html.Label("Select Gharane / Surname (घराणे / आडनाव निवडा)"),
                html.Br(),
                dcc.RadioItems(
                    # radio_button_selection,
                    options = [
                        {'label' : 'Gharane (घराणे)' , 'value': 'gharane'},
                        {'label' : 'Surname (आडनाव)' , 'value' : 'lastName'}
                    ],
                    value = "gharane",
                    id="gharane_selection_1",
                    # inline=True,
                ),
                html.Br(),
                # html.Br(),
                html.Label("Select Options (पर्याय निवडा)"),
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
            id="dropdown-div-1",
            children=[
                html.Br(),
                dcc.Dropdown(
                    id="surname_dropdown_1",
                    clearable=True,
                    style={
                        "display": True,
                        "backgroundColor": colors["background"],
                    },
                    placeholder="Select Options",
                    className="zone-dropdown",
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
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        html.H2(
                            children=[
                                "Top 10 States (10 सर्वाधिक निवासी राज्ये) : ",
                                html.Div(
                                    id="States-header", style={"display": "inline"}
                                ),
                            ],
                            style={
                                "margin-bottom": "0px",
                                "textAlign": "center",
                                "color": colors["text"],
                            },
                        ),
                        html.Br(),
                        html.Br(),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "align-items": "center",
                        "backgroundColor": colors["background"],
                    },
                ),
                html.Div(
                    className="six columns",
                    children=[
                        html.H2(
                            children=[
                                "Top 10 Countries (10 सर्वाधिक निवासी राष्ट्रे) : ",
                                html.Div(
                                    id="Country-header", style={"display": "inline"}
                                ),
                            ],
                            style={
                                "margin-bottom": "0px",
                                "textAlign": "center",
                                "color": colors["text"],
                            },
                        ),
                        html.Br(),
                        html.Br(),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "align-items": "center",
                        "backgroundColor": colors["background"],
                    },
                ),
            ],
        ),
        html.Div(
            className="row",
            id="region-datatable-div",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        html.Br(),
                        html.Br(),
                        dash_table.DataTable(
                            id="region-datatable",
                            selected_rows=[],
                            style_header={
                                "backgroundColor": "rgb(30, 30, 30)",
                                "fontWeight": "bold",
                            },
                            style_cell={
                                "backgroundColor": colors["background"],
                                "color": colors["text"],
                                "text-align": "center",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                                "minWidth": "250px",
                                "width": "250px",
                                "maxWidth": "250px",
                            },
                            fill_width=False,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "align-items": "center",
                        "backgroundColor": colors["background"],
                    },
                ),
                html.Div(
                    className="six columns",
                    children=[
                        html.Br(),
                        html.Br(),
                        dash_table.DataTable(
                            id="region-datatable-country",
                            selected_rows=[],
                            style_header={
                                "backgroundColor": "rgb(30, 30, 30)",
                                "fontWeight": "bold",
                            },
                            style_cell={
                                "backgroundColor": colors["background"],
                                "color": colors["text"],
                                "text-align": "center",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                                "minWidth": "250px",
                                "width": "250px",
                                "maxWidth": "250px",
                            },
                            fill_width=False,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "align-items": "center",
                        "backgroundColor": colors["background"],
                    },
                ),
            ],
            style={
                "backgroundColor": colors["background"],
            },
        ),
    ]
)

@callback(
    Output("surname_dropdown_1", "options"),
    Output("surname_dropdown_1", "value"),
    Input('update-interval-2', 'n_intervals'),
    Input("gharane_selection_1", "value"),
)
def update_radio_button_selection(n_intervals, gharane_selection_1):
    cur.execute(gharane_lastname)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['gharane','lastName','gharane_m','last_name_m'])
    main_df['gharane_m_e'] = main_df['gharane'] + ' (' + main_df['gharane_m'] + ')'
    main_df['last_name_m_e'] = main_df['lastName'] + ' (' + main_df['last_name_m'] + ')'

    if gharane_selection_1 == "gharane":
        options = [
            {"label": i, "value": j}
            for i,j in zip(np.append(["All (सर्व)"], main_df["gharane_m_e"].unique()),np.append(["All"], main_df["gharane"].unique()))
        ]
        value = "All"
    else:
        options = [
            {"label": i, "value": j}
            for i,j in zip(np.append(["All (सर्व)"], main_df["last_name_m_e"].unique()),np.append(["All"], main_df["lastName"].unique()))
        ]
        value = "All"
    return options, value

@callback(
    Output(component_id="region-datatable", component_property="data"),
    Output(component_id="region-datatable-country", component_property="data"),
    Output(component_id="States-header", component_property="children"),
    Output(component_id="Country-header", component_property="children"),
    Input("gharane_selection_1", "value"),
    Input(component_id="surname_dropdown_1", component_property="value"),
    Input('update-interval-2', 'n_intervals'),
)
def update_region_datatable(radio_selection_value, value, n_intervals):
    cur.execute(country_state_sql)
    source_data = cur.fetchall()

    main_df = pd.DataFrame(source_data, columns=['id','gharane','lastName', 'familySize',"provinceOrState", "country","provinceOrState_m", "country_m"])

    if value != 'All':
        main_df = main_df[main_df[radio_selection_value] == value]

    cur.execute(gharane_lastname)
    header_data = cur.fetchall()

    header_data = pd.DataFrame(header_data, columns=['gharane','lastName','gharane_m','last_name_m'])

    tab1 = states_datatable(value, main_df)
    tab2 = country_datatable(value, main_df)
    tab3 = header_value(header_data, value, radio_selection_value)
    # tab4 = header_value(value)
    tab4 = tab3

    return tab1, tab2, tab3, tab4