import dash
from dash import dash_table, dcc, callback, Input, Output

from dash import html

import warnings
import pandas as pd
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=(SettingWithCopyWarning))

import numpy as np
from config import connect
from scripts.retrieve_queries import gharane_lastname, common_names_sql


colors = {"background": "#111111", "text": "#7FDBFF"}

dash.register_page(__name__, name="Names", path="/names")

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

def most_common_names(value, source_data):

    source_data['firstNameM'] = source_data['firstNameM'].apply(lambda x: x.upper())
    
    source_data = source_data.applymap(lambda x: x.strip() if type(x) == str else x)
    source_data['fname'] = source_data['firstname'] + ' (' + source_data['firstNameM'] + ')'
    df = source_data[source_data["gender"] == "Male"]

    most_common_names = (
        df.groupby(["fname"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'fname': 'NAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_daughter_names(value, source_data):
    
    source_data['fullName'] = source_data['fullName'].apply(lambda x: x.upper())

    df = source_data[source_data["gender"] == "Female (Daughter)"]
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)

    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    
    df = df[df['firstName'] != 'DAUGHTER']
    

    df['fname'] = df['firstname'].str.title() + ' (' + df['firstNameM'] + ')'

    most_common_names = (
        df.groupby(["fname"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'fname': 'NAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df

def most_common_daughter_in_law_names(value, source_data):

    source_data['fullName'] = source_data['fullName'].apply(lambda x: x.upper())
    df = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    df = df.applymap(lambda x: x.strip() if type(x) == str else x)

    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    df = df[df['firstName'] != 'WIFE']

    df['fname'] = df['firstname'].str.title() + ' (' + df['firstNameM'] + ')'
    most_common_names = (
        df.groupby(["fname"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'fname': 'NAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_maiden_names(value, source_data):
    source_data = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    source_data = source_data.applymap(lambda x: x.strip() if type(x) == str else x)
    df = source_data[(source_data["maritalFirstNameM"] != "")]
    df['fullName'] = df['fullName'].str.upper()
    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    df = df[df['firstName'] != 'WIFE']
    
    df["maritalFirstNameM"] = df["maritalFirstNameM"].str.upper()
    
    most_common_names = df.groupby(["maritalFirstNameM"])[
        "id"].count().reset_index()

    most_common_names = most_common_names.rename(
        columns={"maritalFirstNameM": "FIRST_NAME", "id": "COUNTS"}
    )

    final_df = most_common_names.sort_values(by=["COUNTS"], ascending=False)
    final_df = final_df.head(10)

    ret_df = final_df.to_dict("records")
    return ret_df

def most_common_daughter_married_surnames(value, source_data):

    source_data = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    source_data = source_data.applymap(lambda x: x.strip() if type(x) == str else x)
    df = source_data[source_data['maritalLastNameM'] != '']
    df['maritalLastNameM'] = df['maritalLastNameM'].str.upper()
    
    most_common_names = (
        df.groupby(["maritalLastNameM"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'maritalLastNameM': 'SURNAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_maiden_surnames(value, source_data):
    source_data = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    source_data = source_data.applymap(lambda x: x.strip() if type(x) == str else x)
    df = source_data[(source_data["maritalLastNameM"] != "")]
    df['fullName'] = df['fullName'].str.upper()
    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    df = df[df['firstName'] != 'WIFE']
    
    df["maritalFirstNameM"] = df["maritalLastNameM"].str.upper()
    
    most_common_names = df.groupby(["maritalLastNameM"])[
        "id"].count().reset_index()

    most_common_names = most_common_names.rename(
        columns={"maritalLastNameM": "LAST_NAME", "id": "COUNTS"}
    )

    final_df = most_common_names.sort_values(by=["COUNTS"], ascending=False)
    final_df = final_df.head(10)

    ret_df = final_df.to_dict("records")
    return ret_df


def header_value(header_data, value, radio_selection_value):
    if value == 'All':
        # return [f"{value}"]
        return "All (सर्व)"
    else:
        if radio_selection_value == 'gharane':
            gharane_header = header_data[header_data['gharane'] == value]
            gharane_header = gharane_header['gharane'] + ' (' + gharane_header['gharane_m'] + ')'
            gharane_header = gharane_header.tolist()
            
            return [f"{gharane_header[0]}"]
        else:
            surname_header = header_data[header_data['lastName'] == value]
            surname_header = surname_header['lastName'] + ' (' + surname_header['last_name_m'] + ')'
            surname_header = surname_header.tolist()
            
            return [f"{surname_header[0]}"]


layout = html.Div([
    dcc.Tabs(id = 'tabs', value = 'first_names_tab', children = [
        dcc.Tab(label = 'First Names (नाव)', value = 'first_names_tab' , style=tab_style, selected_style=tab_selected_style, 
                children = [
                    html.Div(
            [
                dcc.Interval(
                id='update-interval-3',
                interval=86400 * 1000, # in milliseconds
                n_intervals=0
                ),
                html.Div(
                        [
                            html.Div(
                                [html.Br(),
                                    html.Div(
                                        [
                                            html.H1(
                                                "Top 10 First Names (सर्वाधिक लोकप्रिय 10 नावे)",
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
                                options = [
                                    {'label' : 'Gharane (घराणे)' , 'value': 'gharane'},
                                    {'label' : 'Surname (आडनाव)' , 'value' : 'lastName'}
                                ],
                                value = "gharane",
                                id="gharane_selection_2",
                                # inline=True,
                            ),
                            html.Br(),
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
                        id="dropdown-div-2",
                        children=[
                            html.Br(),
                            dcc.Dropdown(
                                id="surname_dropdown_2",
                                clearable=True,
                                style={
                                    "display": True,
                                    "backgroundColor": colors["background"],
                                },
                                placeholder="Select Options",
                                className="zone-dropdown-1",
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
                                            "Males (पुरुष) : ",
                                            html.Div(
                                                id="male-names-header", style={"display": "inline"}
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
                                            "Daughters (कन्या) : ",
                                            html.Div(
                                                id="daughter-names-header", style={"display": "inline"}
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
                    id="names-datatable-div",
                    children=[
                        html.Div(
                            className="six columns",
                            children=[
                                html.Br(),
                                html.Br(),
                                dash_table.DataTable(
                                    id="male-names-datatable",
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
                                        'border': '1px solid gray'
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
                                    id="daughter-names-datatable",
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
                                        'border': '1px solid gray'
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
                html.Div(
                        children = [
                                    html.Br()
                                    ]
                        ),
                html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="six columns",
                                children=[
                                    html.H2(
                                        children=[
                                            "Daughters-in-Law (स्नुषा) : ",
                                            html.Div(
                                                id="daughterinlaw-names-header", style={"display": "inline"}
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
                                            "Daughters-in-Law (Maiden) (स्नुषा माहेर) : ",
                                            html.Div(
                                                id="maiden-names-header", style={"display": "inline"}
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
                    id="names-datatable-div-1",
                    children=[
                        html.Div(
                            className="six columns",
                            children=[
                                html.Br(),
                                html.Br(),
                                dash_table.DataTable(
                                    id="daughterinlaw-names-datatable",
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
                                        'border': '1px solid gray'
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
                                        id="maiden-names-datatable",
                                        selected_rows=[],
                                        style_header={
                                            "backgroundColor": "rgb(30, 30, 30)",
                                            "fontWeight": "bold",
                                        },
                                        style_cell={
                                            'padding-right': '30px',
                                            'padding-left': '30px',
                                            "backgroundColor": colors["background"],
                                            "color": colors["text"],
                                            "text-align": "center",
                                            "marginLeft": "auto",
                                            "marginRight": "auto",
                                            "minWidth": "250px",
                                            "width": "250px",
                                            "maxWidth": "250px",
                                            'border': '1px solid gray'
                                        },
                                        fill_width=False,
                                    )
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
                )

            ]
        )
        
                ]),
        dcc.Tab(label = 'Last Names (आडनाव)', value = 'surnames_tab', style=tab_style, selected_style=tab_selected_style,
                children = [
                    html.Div([
                                dcc.Interval(
                                id='update-interval-4',
                                interval=86400 * 1000, # in milliseconds
                                n_intervals=0
                                ),
                        html.Div(
                                [
                                    html.Div(
                                        [html.Br(),
                                            html.Div(
                                                [
                                                    html.H1(
                                                        "Top 10 Last Names (सर्वाधिक लोकप्रिय 10 आडनावे)",
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
                                        options = [
                                            {'label' : 'Gharane (घराणे)' , 'value': 'gharane'},
                                            {'label' : 'Surname (आडनाव)' , 'value' : 'lastName'}
                                        ],
                                        value = "gharane",
                                        id="gharane_selection_3",
                                        # inline=True,
                                    ),
                                    html.Br(),
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
                                id="dropdown-div-3",
                                children=[
                                    html.Br(),
                                    dcc.Dropdown(
                                        id="surname_dropdown_3",
                                        clearable=True,
                                        style={
                                            "display": True,
                                            "backgroundColor": colors["background"],
                                        },
                                        placeholder="Select Options",
                                        className="zone-dropdown-2",
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
                                                "Daughters-in-Law Surnames (स्नुषा आडनाव) : ",
                                                html.Div(
                                                    id="married-surnames-header", style={"display": "inline"}
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
                                                "Daughters-in-Law Maiden Surnames (स्नुषा माहेरी आडनाव)",
                                                html.Div(
                                                    id="married-maiden-surnames-header", style={"display": "inline"}
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
                            id="names-datatable-div-2",
                            children=[
                                html.Div(
                                    className="six columns",
                                    children=[
                                        html.Br(),
                                        html.Br(),
                                        dash_table.DataTable(
                                            id="married-surnames-datatable",
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
                                                'border': '1px solid gray'
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
                                            id="married-maiden-surnames-datatable",
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
                                                'border': '1px solid gray'
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
                        )
                    ])
                ]),
    ]),
    html.Div(id = 'tab-content')
])


@callback(
    Output("surname_dropdown_2", "options"),
    Output("surname_dropdown_2", "value"),
    Input('update-interval-3', 'n_intervals'),
    Input("gharane_selection_2", "value"),
)
def update_radio_button_selection(n_intervals, gharane_selection_2):
    cur.execute(gharane_lastname)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['gharane','lastName','gharane_m','last_name_m'])
    main_df['gharane_m_e'] = main_df['gharane'] + ' (' + main_df['gharane_m'] + ')'
    main_df['last_name_m_e'] = main_df['lastName'] + ' (' + main_df['last_name_m'] + ')'

    if gharane_selection_2 == "gharane":
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
    Output("surname_dropdown_3", "options"),
    Output("surname_dropdown_3", "value"),
    Input('update-interval-4', 'n_intervals'),
    Input("gharane_selection_3", "value")
)
def update_radio_button_selection(n_intervals_1, gharane_selection_3):
    cur.execute(gharane_lastname)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['gharane','lastName','gharane_m','last_name_m'])
    main_df['gharane_m_e'] = main_df['gharane'] + ' (' + main_df['gharane_m'] + ')'
    main_df['last_name_m_e'] = main_df['lastName'] + ' (' + main_df['last_name_m'] + ')'

    if gharane_selection_3 == "gharane":
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
    Output(component_id="male-names-header", component_property="children"),
    Output(component_id="daughter-names-header", component_property="children"),
    Output(component_id="daughterinlaw-names-header",component_property="children"),
    Output(component_id="maiden-names-header",component_property="children"),

    Output(component_id="male-names-datatable", component_property="data"),
    Output(component_id="daughter-names-datatable", component_property="data"),
    Output(component_id="daughterinlaw-names-datatable",component_property="data"),
    Output(component_id="maiden-names-datatable",component_property="data"),

    Output(component_id="married-surnames-header",component_property="children"),
    Output(component_id="married-maiden-surnames-header",component_property="children"),
    Output(component_id="married-surnames-datatable",component_property="data"),
    Output(component_id="married-maiden-surnames-datatable",component_property="data"),

    Input("gharane_selection_2", "value"),
    Input("gharane_selection_3", "value"),
    Input(component_id="surname_dropdown_2", component_property="value"),
    Input(component_id="surname_dropdown_3", component_property="value"),
    Input('update-interval-3', 'n_intervals'),
    Input('update-interval-4', 'n_intervals_1')
)
def update_surname_table(radio_selection_value, radio_selection_value_1,  value, value_1, n_intervals, n_intervals_1):
    cur.execute(common_names_sql)
    source_data = cur.fetchall()

    main_df_fnames = pd.DataFrame(source_data, columns=['id', 'gharane', 'lastName','family_size','gender', 'fullName', 'firstname', 
                                                        'firstNameM', 'maritalLastNameM','maritalFirstNameM'])
    main_df_lnames = main_df_fnames
    
    if value != 'All':
        main_df_fnames = main_df_fnames[main_df_fnames[radio_selection_value] == value]

    if value_1 != 'All':
        main_df_lnames = main_df_lnames[main_df_lnames[radio_selection_value_1] == value_1]

    cur.execute(gharane_lastname)
    header_data = cur.fetchall()

    header_data = pd.DataFrame(header_data, columns=['gharane','lastName','gharane_m','last_name_m'])

    tab1 = header_value(header_data, value, radio_selection_value)
    
    tab2 = tab1
    tab3 = tab1
    tab4 = tab1

    tab5 = most_common_names(value, main_df_fnames)
    tab6 = most_common_daughter_names(value, main_df_fnames)
    tab7 = most_common_daughter_in_law_names(value, main_df_fnames)
    tab8 = most_common_maiden_names(value, main_df_fnames)

    tab9 = header_value(header_data, value_1, radio_selection_value_1)
    # tab10 = header_value(header_data, value_1, radio_selection_value_1)
    tab10 = tab9

    tab11 = most_common_daughter_married_surnames(value_1, main_df_lnames)
    tab12 = most_common_maiden_surnames(value_1, main_df_lnames)
    
    return tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12