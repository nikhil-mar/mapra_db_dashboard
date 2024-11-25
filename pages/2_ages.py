import dash
from dash import dash_table,dcc, callback, Input, Output

from dash import html

import pandas as pd
import numpy as np
import datetime
import plotly.express as px
from config import connect
from scripts.retrieve_queries import gharane_lastname, age_group_sql, oldest_individual_sql, youngest_individual_sql, avg_ages

colors = {"background": "#111111", "text": "#7FDBFF"}

dash.register_page(__name__, name="Ages", path="/ages")

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
    fig.update_traces(textposition="outside",marker_color='mediumpurple')
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        # plot_bgcolor='#800080',
        font_color=colors["text"],
        xaxis={"showgrid": False},
        yaxis={"showgrid": False},
        yaxis_title="Individuals (व्यक्ती)",
        xaxis_title="Age Groups (वयोगट)",
        font=dict(size=14)
    )

    return fig

def oldest_individual(source_data):

    # 'surname_m', 'last_name','age','gender','first_name_m','first_name','middle_name_m','middle_name',
    #                                         'last_name_m','gharane_m', 'gharane','gharane_id','pidhi'

    oldest_male = source_data[source_data['gender'] == 'Male']
    oldest_male['surname'] = oldest_male['last_name'] + ' (' + oldest_male['surname_m'] + ')'
    oldest_male['name'] = oldest_male['first_name'] + ' ' + oldest_male['middle_name'] +' (' + oldest_male['first_name_m'] + ' ' + oldest_male['middle_name_m'] + ')'
    oldest_male['gharane'] = oldest_male['gharane'] + ' (' + oldest_male['gharane_m'] + ')'
    oldest_male = oldest_male[['surname','age','name','gharane','pidhi']]
    oldest_male = oldest_male.rename(
        columns={'surname': 'Surname (आडनाव)', "age": "Age (वय)", "name":"Name (नाव)", "gharane":"Gharane (घराणे)", "pidhi" : "Generation (पिढी)"})
    
    final_oldest_male = oldest_male.to_dict("records")

    oldest_daughter = source_data[source_data['gender'] == 'Female (Daughter)']
    oldest_daughter['surname'] = oldest_daughter['last_name'] + ' (' + oldest_daughter['surname_m'] + ')'
    oldest_daughter['name'] = oldest_daughter['first_name'] + ' ' + oldest_daughter['middle_name'] +' (' + oldest_daughter['first_name_m'] + ' ' + oldest_daughter['middle_name_m'] + ')'
    oldest_daughter['gharane'] = oldest_daughter['gharane'] + ' (' + oldest_daughter['gharane_m'] + ')'
    oldest_daughter = oldest_daughter[['surname','age','name','gharane','pidhi']]
    oldest_daughter = oldest_daughter.rename(
        columns={'surname': 'Surname (आडनाव)', "age": "Age (वय)", "name":"Name (नाव)", "gharane":"Gharane (घराणे)", "pidhi" : "Generation (पिढी)"})
    
    final_oldest_daughter = oldest_daughter.to_dict("records")

    oldest_dil = source_data[source_data['gender'] == 'Female (Daughter in Law)']
    oldest_dil['surname'] = oldest_dil['last_name'] + ' (' + oldest_dil['surname_m'] + ')'
    oldest_dil['name'] = oldest_dil['first_name'] + ' ' + oldest_dil['middle_name'] +' (' + oldest_dil['first_name_m'] + ' ' + oldest_dil['middle_name_m'] + ')'
    oldest_dil['gharane'] = oldest_dil['gharane'] + ' (' + oldest_dil['gharane_m'] + ')'
    oldest_dil = oldest_dil[['surname','age','name','gharane','pidhi']]
    oldest_dil = oldest_dil.rename(
        columns={'surname': 'Surname (आडनाव)', "age": "Age (वय)", "name":"Name (नाव)", "gharane":"Gharane (घराणे)", "pidhi" : "Generation (पिढी)"})
    final_oldest_dil = oldest_dil.to_dict("records")

    return final_oldest_male, final_oldest_daughter, final_oldest_dil

def youngest_individual(source_data):
    youngest_male = source_data[source_data['gender'] == 'Male']
    youngest_male['surname'] = youngest_male['last_name'] + ' (' + youngest_male['surname_m'] + ')'
    youngest_male['name'] = youngest_male['first_name'] + ' ' + youngest_male['middle_name'] +' (' + youngest_male['first_name_m'] + ' ' + youngest_male['middle_name_m'] + ')'
    youngest_male['gharane'] = youngest_male['gharane'] + ' (' + youngest_male['gharane_m'] + ')'
    youngest_male = youngest_male[['surname','age','name','gharane','pidhi']]
    youngest_male = youngest_male.rename(
        columns={'surname': 'Surname (आडनाव)', "age": "Age (वय)", "name":"Name (नाव)", "gharane":"Gharane (घराणे)", "pidhi" : "Generation (पिढी)"})
    final_youngest_male = youngest_male.to_dict("records")

    youngest_daughter = source_data[source_data['gender'] == 'Female (Daughter)']
    youngest_daughter['surname'] = youngest_daughter['last_name'] + ' (' + youngest_daughter['surname_m'] + ')'
    youngest_daughter['name'] = youngest_daughter['first_name'] + ' ' + youngest_daughter['middle_name'] +' (' + youngest_daughter['first_name_m'] + ' ' + youngest_daughter['middle_name_m'] + ')'
    youngest_daughter['gharane'] = youngest_daughter['gharane'] + ' (' + youngest_daughter['gharane_m'] + ')'
    youngest_daughter = youngest_daughter[['surname','age','name','gharane','pidhi']]
    youngest_daughter = youngest_daughter.rename(
        columns={'surname': 'Surname (आडनाव)', "age": "Age (वय)", "name":"Name (नाव)", "gharane":"Gharane (घराणे)", "pidhi" : "Generation (पिढी)"})
    final_youngest_daughter = youngest_daughter.to_dict("records")

    youngest_dil = source_data[source_data['gender'] == 'Female (Daughter in Law)']
    youngest_dil['surname'] = youngest_dil['last_name'] + ' (' + youngest_dil['surname_m'] + ')'
    youngest_dil['name'] = youngest_dil['first_name'] + ' ' + youngest_dil['middle_name'] +' (' + youngest_dil['first_name_m'] + ' ' + youngest_dil['middle_name_m'] + ')'
    youngest_dil['gharane'] = youngest_dil['gharane'] + ' (' + youngest_dil['gharane_m'] + ')'
    youngest_dil = youngest_dil[['surname','age','name','gharane','pidhi']]
    youngest_dil = youngest_dil.rename(
        columns={'surname': 'Surname (आडनाव)', "age": "Age (वय)", "name":"Name (नाव)", "gharane":"Gharane (घराणे)", "pidhi" : "Generation (पिढी)"})
    final_youngest_dil = youngest_dil.to_dict("records")

    return final_youngest_male, final_youngest_daughter, final_youngest_dil

def average_ages(source_data):
    
    tmp = source_data.select_dtypes(include=[np.number])
    source_data.loc[:, tmp.columns] = np.round(tmp,2)
    source_data['surname'] = source_data['last_name'] + ' (' + source_data['last_name_m'] + ')'
    source_data = source_data[['surname','males','daughters','daughters_in_law']]
    source_data = source_data.rename(
        columns={'surname': 'Surname (आडनाव)', "males": "Males (पुरुष)", "daughters":"Daughters (कन्या)", "daughters_in_law":"Daughters-in-Law (स्नुषा)"})
    avg_ages = source_data.to_dict('records')
    return avg_ages

layout = html.Div(
    [   dcc.Interval(
        id='update-interval-1',
        interval=86400 * 1000, # in milliseconds
        n_intervals=0
        ),
        dcc.Tabs(id = 'tabs', value = 'age_group_distribution', children = [
            dcc.Tab(label = 'Age Group Analysis-Living Persons (जीवित व्यक्तींचे वयोगट)', value = 'age_group_distribution' , style=tab_style, selected_style=tab_selected_style, 
                children = [
                    html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [html.Br(),
                                                    html.H1(
                                                        "Age Group Analysis-Living Persons (जीवित व्यक्तींचे वयोगट)",
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
                                        id="gharane_selection",
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
                                id="dropdown-div",
                                children=[
                                    # html.Br(),
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
                ]),
            dcc.Tab(label = 'Oldest Living Person (सर्वात वयस्क व्यक्ती)', value = 'oldest_person' , style=tab_style, selected_style=tab_selected_style, 
                children = [
                    html.Br(),
                    html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    children=[
                                        
                                        html.H2(
                                            children=[
                                                "Males (पुरुष)",
                                                html.Div(
                                                    id="oldest_male_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),
                                        
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="oldest-male-datatable-div",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Br(),
                                                dash_table.DataTable(
                                                    id="oldest-male-datatable",
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
                                                        "maxWidth": "500px",
                                                        'border': '1px solid gray'
                                                    },
                                                    # style_table={'overflowX': 'auto'},
                                                    fill_width=True,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "backgroundColor": colors["background"],
                                            },
                                        ),
                                        
                                    ]
                                ),
                                html.Div(
                                    children = [
                                        html.Br()
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.H2(
                                            children=[
                                                "Daughters (कन्या)",
                                                html.Div(
                                                    id="oldest_daughter_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="oldest-daughter-datatable-div",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Br(),
                                                dash_table.DataTable(
                                                    id="oldest-daughter-datatable",
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
                                                        "maxWidth": "550px",
                                                        'border': '1px solid gray'
                                                    },
                                                    # style_table={'overflowX': 'auto'},
                                                    fill_width=True,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "backgroundColor": colors["background"],
                                            },
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children = [
                                        html.Br()
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.H2(
                                            children=[
                                                "Daughters in Law (स्नुषा)",
                                                html.Div(
                                                    id="oldest_daughter_in_law_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),

                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="oldest-daughter-in-law-datatable-div",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Br(),
                                                dash_table.DataTable(
                                                    id="oldest-daughter-in-law-datatable",
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
                                                        "maxWidth": "500px",
                                                        'border': '1px solid gray'
                                                    },
                                                    # style_table={'overflowX': 'auto'},
                                                    fill_width=True,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "backgroundColor": colors["background"],
                                            },
                                        )
                                    ]
                                )
                            ]
                    )
                ]),
            dcc.Tab(label = 'Youngest Living Person (सर्वात तरुण व्यक्ती)', value = 'youngest_person' , style=tab_style, selected_style=tab_selected_style, 
                children = [
                    html.Br(),
                    html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    children=[
                                        html.H2(
                                            children=[
                                                "Males (पुरुष)",
                                                html.Div(
                                                    id="youngest_male_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="youngest-male-datatable-div",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Br(),
                                                dash_table.DataTable(
                                                    id="youngest-male-datatable",
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
                                                        "maxWidth": "500px",
                                                        'border': '1px solid gray'
                                                    },
                                                    # style_table={'overflowX': 'auto'},
                                                    fill_width=True,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "backgroundColor": colors["background"],
                                            },
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children = [
                                        html.Br()
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Br(),
                                        html.Br(),
                                        html.H2(
                                            children=[
                                                "Daughter (कन्या)",
                                                html.Div(
                                                    id="youngest_daughter_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="youngest-daughter-datatable-div",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Br(),
                                                dash_table.DataTable(
                                                    id="youngest-daughter-datatable",
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
                                                        "maxWidth": "500px",
                                                        'border': '1px solid gray'
                                                    },
                                                    # style_table={'overflowX': 'auto'},
                                                    fill_width=True,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "backgroundColor": colors["background"],
                                            },
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children = [
                                        html.Br()
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.H2(
                                            children=[
                                                "Daughters in Law (स्नुषा)",
                                                html.Div(
                                                    id="youngest_daughter_in_law_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="youngest-daughter-in-law-datatable-div",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Br(),
                                                dash_table.DataTable(
                                                    id="youngest-daughter-in-law-datatable",
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
                                                        "maxWidth": "500px",
                                                        'border': '1px solid gray'
                                                    },
                                                    # style_table={'overflowX': 'auto'},
                                                    fill_width=True,
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                                "backgroundColor": colors["background"],
                                            },
                                        )
                                    ]
                                )
                            ]
                    )
                ]),
            dcc.Tab(label = 'Average Ages-Living Persons (सरासरी वये - जीवित व्यक्ती)', value = 'average_ages' , style=tab_style, selected_style=tab_selected_style, 
                children = [
                    html.Br(),
                    html.Div(
                        children = [
                            html.Div(
                                    children=[
                                        html.H2(
                                            children=[
                                                "Average Ages (सरासरी वये)",
                                                html.Div(
                                                    id="average_ages_header", style={"display": "inline"}
                                                ),
                                            ],
                                            style={
                                                "margin-bottom": "0px",
                                                "textAlign": "center",
                                                "color": colors["text"],
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "align-items": "center",
                                        "backgroundColor": colors["background"],
                                    },
                                ),
                                html.Br(),
                                html.Div(
                                    className="row",
                                    id="average-ages-datatable-div",
                                    children=[
                                        
                                        html.Div(
                                            children=[
                                                dash_table.DataTable(
                                                    id="average-ages-datatable",
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
                                    ]
                                )
                        ]
                    )
                ])
        ]),
        html.Div(id = 'tab-content-ages')
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
    main_df = pd.DataFrame(source_data, columns=['gharane','lastName','gharane_m','last_name_m'])
    main_df['gharane_m_e'] = main_df['gharane'] + ' (' + main_df['gharane_m'] + ')'
    main_df['last_name_m_e'] = main_df['lastName'] + ' (' + main_df['last_name_m'] + ')'

    if gharane_selection == "gharane":
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
    Output(component_id="birth-periods-graph", component_property="figure"),
    Output(component_id="oldest-male-datatable", component_property="data"),
    Output(component_id="oldest-daughter-datatable", component_property="data"),
    Output(component_id="oldest-daughter-in-law-datatable", component_property="data"),
    Output(component_id="youngest-male-datatable", component_property="data"),
    Output(component_id="youngest-daughter-datatable", component_property="data"),
    Output(component_id="youngest-daughter-in-law-datatable", component_property="data"),
    Output(component_id="average-ages-datatable", component_property="data"),
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

    cur.execute(oldest_individual_sql)
    data = cur.fetchall()

    main_data = pd.DataFrame(data, columns=['surname_m', 'last_name','age','gender','first_name_m','first_name','middle_name_m','middle_name',
                                            'last_name_m','gharane_m', 'gharane','gharane_id','pidhi'])
    tab1 = oldest_individual(main_data)

    cur.execute(youngest_individual_sql)
    data = cur.fetchall()
    main_data = pd.DataFrame(data, columns=['surname_m', 'last_name','age','gender','first_name_m','first_name','middle_name_m','middle_name',
                                            'last_name_m','gharane_m', 'gharane','gharane_id','pidhi'])
    tab2 = youngest_individual(main_data)

    cur.execute(avg_ages)
    data = cur.fetchall()
    main_data = pd.DataFrame(data, columns=['last_name_m','last_name','males','daughters','daughters_in_law'])
    tab3 = average_ages(main_data)

    return fig, tab1[0], tab1[1], tab1[2], tab2[0], tab2[1], tab2[2], tab3