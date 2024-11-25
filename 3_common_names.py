import dash
from dash import dash_table, dcc, callback, Input, Output

from dash import html

import pandas as pd
import numpy as np
from config import connect
from scripts.retrieve_queries import gharane_lastname, common_names_sql

colors = {"background": "#111111", "text": "#7FDBFF"}

dash.register_page(__name__, name="Names", path="/common_names")

conn = connect()
cur = conn.cursor()

radio_button_selection = ["gharane", "lastName"]

def most_common_names(value, source_data):

    source_data['firstNameM'] = source_data['firstNameM'].apply(lambda x: x.upper())
    df = source_data[source_data["gender"] == "Male"]
    most_common_names = (
        df.groupby(["firstNameM"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'firstNameM': 'NAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_daughter_names(value, source_data):
    
    source_data['fullName'] = source_data['fullName'].apply(lambda x: x.upper())
    df = source_data[source_data["gender"] == "Female (Daughter)"]
    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    df = df[df['firstName'] != 'DAUGHTER']
    most_common_names = (
        df.groupby(["firstNameM"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'firstNameM': 'NAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_daughter_in_law_names(value, source_data):

    source_data['fullName'] = source_data['fullName'].apply(lambda x: x.upper())
    df = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    df = df[df['firstName'] != 'WIFE']
    most_common_names = (
        df.groupby(["firstNameM"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'firstNameM': 'NAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_married_surnames(value, source_data):

    source_data = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    df = source_data[source_data['maritalLastNameM'] != '']
    df['maritalLastNameM'] = df['maritalLastNameM'].str.upper()
    
    most_common_names = (
        df.groupby(["maritalLastNameM"])["id"].count().reset_index()
    )
    most_common_names = most_common_names.rename(
        columns={'maritalLastNameM': 'SURNAME', "id": "COUNTS"})
    final_df = most_common_names.sort_values(by=['COUNTS'], ascending=False)
    final_df = final_df.head(10)
    print(final_df)
    ret_df = final_df.to_dict("records")
    return ret_df


def most_common_maiden_names(value, source_data):
    source_data = source_data[source_data["gender"] == "Female (Daughter in Law)"]
    # df = source_data[(source_data["maritalFirstNameM"] != "")]
    df = source_data[(source_data["maritalLastNameM"] != "")]
    print(df.head())
    df['fullName'] = df['fullName'].str.upper()
    df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
    df = df[df['firstName'] != 'WIFE']
    
    # df["maritalFirstNameM"] = df["maritalFirstNameM"].str.upper()
    df["maritalFirstNameM"] = df["maritalLastNameM"].str.upper()
    
    # most_common_names = df.groupby(["maritalFirstNameM"])[
        # "id"].count().reset_index()
    most_common_names = df.groupby(["maritalLastNameM"])[
        "id"].count().reset_index()

    # most_common_names = most_common_names.rename(
    #     columns={"maritalFirstNameM": "FIRST_NAME", "id": "COUNTS"}
    # )

    most_common_names = most_common_names.rename(
        columns={"maritalLastNameM": "LAST_NAME", "id": "COUNTS"}
    )

    final_df = most_common_names.sort_values(by=["COUNTS"], ascending=False)
    final_df = final_df.head(10)

    print(final_df)

    ret_df = final_df.to_dict("records")
    return ret_df

def header_value(value):
    return [f"{value}"]

layout = html.Div(
    [
        dcc.Interval(
        id='update-interval-3',
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
                                    "Top 10 Name Categories",
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
                    id="gharane_selection_2",
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
                                "Top 10 male names for : ",
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
                                "Top 10 female(daughter) names for : ",
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
            className="row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        html.H2(
                            children=[
                                "Top 10 daughter in law names for : ",
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
                                "Top 10 married surnames for : ",
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
            className='row',
            children= [
                html.Br(),
                html.Br(),
                html.Div(
                    className = 'column xs=12 sm=12 md=2 lg=2 xl=2'
                ),
                html.Div(
                    className = 'column xs=12 sm=12 md=2 lg=2 xl=8',
                    children=
                        [
                            html.H2(
                            children=[
                                "Top 10 maiden names for : ",
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
                        ]
                ),
                html.Div(
                    className = 'column xs=12 sm=12 md=2 lg=2 xl=2'
                ),
                
            ]
        ),
        html.Div(
            className='row',
            
            children= [
                html.Br(),
                html.Br(),
                html.Div(
                    className = 'column xs=12 sm=12 md=2 lg=2 xl=2'
                ),
                html.Div(
                    className = 'column xs=12 sm=12 md=8 lg=8 xl=8',
                    children=
                        [
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
                html.Div(
                    className = 'column xs=12 sm=12 md=2 lg=2 xl=2'
                ),
                
            ]
        )
    ]
)


@callback(
    Output("surname_dropdown_2", "options"),
    Output("surname_dropdown_2", "value"),
    Input('update-interval-3', 'n_intervals'),
    Input("gharane_selection_2", "value")
)
def update_radio_button_selection(n_intervals, gharane_selection_2):
    cur.execute(gharane_lastname)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['gharane','lastName'])

    if gharane_selection_2 == "gharane":
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
    Output(component_id="male-names-header", component_property="children"),
    Output(component_id="daughter-names-header", component_property="children"),
    Output(component_id="male-names-datatable", component_property="data"),
    Output(component_id="daughter-names-datatable", component_property="data"),
    Output(component_id="daughterinlaw-names-header",component_property="children"),
    Output(component_id="married-surnames-header",component_property="children"),
    Output(component_id="daughterinlaw-names-datatable",component_property="data"),
    Output(component_id="married-surnames-datatable",component_property="data"),
    Output(component_id="maiden-names-header",component_property="children"),
    Output(component_id="maiden-names-datatable",component_property="data"),
    Input("gharane_selection_2", "value"),
    Input(component_id="surname_dropdown_2", component_property="value"),
    Input('update-interval-3', 'n_intervals')
)
def update_surname_table(radio_selection_value, value, n_intervals):
    cur.execute(common_names_sql)
    source_data = cur.fetchall()

    main_df = pd.DataFrame(source_data, columns=['id', 'gharane', 'lastName','family_size','gender', 'fullName', 'firstNameM', 'maritalLastNameM','maritalFirstNameM'])
    
    if value != 'All':
        main_df = main_df[main_df[radio_selection_value] == value]

    tab1 = header_value(value)
    tab2 = header_value(value)
    tab3 = most_common_names(value, main_df)
    tab4 = most_common_daughter_names(value, main_df)
    tab5 = header_value(value)
    tab6 = header_value(value)
    tab7 = most_common_daughter_in_law_names(value, main_df)
    tab8 = most_common_married_surnames(value, main_df)
    tab9 = header_value(value)
    tab10 = most_common_maiden_names(value, main_df)

    return tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10