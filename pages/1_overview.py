import dash
from dash import dash_table, dcc, callback, Input, Output
from dash import html
import pandas as pd
import numpy as np
from functools import partial, reduce
import functools
from config import connect
import plotly.express as px
from scripts.retrieve_queries import summary_sql, surnames_m
import dash_bootstrap_components as dbc

dash.register_page(__name__, name="Overview", path="/")
colors = {"background": "#111111", "text": "#7FDBFF"}

conn = connect()
cur = conn.cursor()

def summary_datatable(source_data, surnames_m_df):

    def surname_groupby(source_data, col_name):
        persons = source_data.groupby("lastName")["id"].count().reset_index()
        persons = persons.rename(columns={"id": f"{col_name}"})
        return persons


    def no_of_persons(source_data):
        persons = surname_groupby(source_data, "No. of persons (एकूण व्यक्ती)")
        return persons
    
    def gender_living_status(source_data):
        persons = source_data[["id", "gender", "livingStatus", "lastName"]].query(
            "gender.notnull()"
        )

        persons["gender_new"] = np.where(
            persons["gender"] == "Male",
            "Male",
            np.where(persons["gender"] != "Male", "Female", np.nan),
        )

        persons["livingStatus_new"] = np.where(
            persons["livingStatus"] == "Expired",
            "Expired",
            np.where(persons["livingStatus"] == "Living", "Living", "Unknown"),
        )

        return persons
    
    gender_living = gender_living_status(source_data)

    def males_living(gender_living):
        males_living = gender_living[
        (gender_living["gender_new"] == "Male") & (gender_living["livingStatus_new"] == "Living")
        ]
        males_living = surname_groupby(males_living, "Males-Living (पुरुष-जीवित)")
        return males_living
    

    def males_dead(gender_living):
        males_dead = gender_living[
            (gender_living["gender_new"] == "Male") & (
                gender_living["livingStatus_new"] == "Expired")
        ]
        males_dead = surname_groupby(males_dead, "Males-Dead (पुरुष-मृत)")
        return males_dead


    def females_living(gender_living):
        females_living = gender_living[
            (gender_living["gender_new"] == "Female") & (
                gender_living["livingStatus_new"] == "Living")
        ]
        females_living = surname_groupby(females_living, "Females-Living (स्त्रिया-जीवित)")
        return females_living


    def females_dead(gender_living):
        females_dead = gender_living[
            (gender_living["gender_new"] == "Female") & (
                gender_living["livingStatus_new"] == "Expired")
        ]
        females_dead = surname_groupby(females_dead, "Females-Dead (स्त्रिया-मृत)")
        return females_dead


    def married(source_data):
        married_persons = source_data[source_data["maritalStatus"] == "Married"]
        married_persons = surname_groupby(married_persons, "Married Individuals (विवाहित व्यक्ती)")
        return married_persons


    def unmarried(source_data):
        unmarried_persons = source_data[source_data["maritalStatus"] == "Unmarried"]
        unmarried_persons = surname_groupby(
            unmarried_persons, "UnMarried Individuals (अविवाहित व्यक्ती)")
        return unmarried_persons


    def family_size(source_data):

        df1 = source_data[["lastName", "gharaneId"]].drop_duplicates()
        surname_wise_gharanes = df1.groupby("lastName")["gharaneId"].nunique()

        source_data["gender_new"] = np.where(
            source_data["gender"] == "Male",
            "Male",
            np.where(source_data["gender"] != "Male", "Female", np.nan),
        )

        females = source_data[source_data["gender_new"] == "Female"]
        total_females = females.groupby("lastName")["gender_new"].count()

        males = source_data[source_data["gender_new"] == "Male"]
        married_males = males[males["maritalStatus"] == "Married"]
        unmarried_males = males[males["maritalStatus"] != "Married"]

        total_married_males = married_males.groupby(
            "lastName")["maritalStatus"].count()

        total_unmarried_males = unmarried_males.groupby(
            "lastName")["maritalStatus"].count()

        final_df = [
            surname_wise_gharanes,
            total_females,
            total_married_males,
            total_unmarried_males,
        ]

        final_df = functools.reduce(
            lambda left, right: pd.merge(left, right, on="lastName"), final_df
        )

        final_df = final_df.reset_index()
        final_df = final_df.rename(
            columns={
                "gharaneId": "gharanes",
                "gender_new": "females",
                "maritalStatus_x": "marriedMales",
                "maritalStatus_y": "unmarriedMales",
            }
        )

        final_df["familySize (कुटुंब सदस्यसंख्या)"] = (
            final_df["females"]
            + 2 * final_df["marriedMales"]
            + final_df["unmarriedMales"]
            - final_df["gharanes"]
        # ) / (final_df["marriedMales"] + final_df["unmarriedMales"])
        ) / final_df["marriedMales"]
        final_df["familySize (कुटुंब सदस्यसंख्या)"] = final_df["familySize (कुटुंब सदस्यसंख्या)"].apply(
            lambda x: round(x, 2))

        final_df = final_df[['lastName', 'familySize (कुटुंब सदस्यसंख्या)']]

        return final_df


    def life_span(source_data):
        source_data["birthDate"] = pd.to_datetime(source_data["birthDate"], errors="coerce")
        source_data["deathDate"] = pd.to_datetime(source_data["deathDate"], errors="coerce")

        new_df = source_data[(source_data.birthDate.notnull()) & (source_data.deathDate.notnull())]

        new_df = new_df[["id", "lastName", "birthDate", "deathDate"]]
        new_df["age"] = new_df["deathDate"].dt.year - new_df["birthDate"].dt.year
        new_df["age"] -= (
            (new_df["deathDate"].dt.month * 32 + new_df["deathDate"].dt.day)
            - (new_df["birthDate"].dt.month * 32 + new_df["birthDate"].dt.day)
        ).apply(lambda x: 1 if x < 0 else 0)

        avglifespan = new_df.groupby("lastName")["age"].mean()
        avglifespan = avglifespan.reset_index()
        avglifespan = avglifespan.rename(columns={"age": "avglifespan (सरासरी आयुष्मान)"})

        return avglifespan

    dfs = [
        no_of_persons(source_data),
        males_living(gender_living),
        males_dead(gender_living),
        females_living(gender_living),
        females_dead(gender_living),
        married(source_data),
        unmarried(source_data),
        family_size(source_data),
        life_span(source_data),
    ]

    merge = partial(pd.merge, on=["lastName"], how="outer")
    
    merge = reduce(merge, dfs)

    merge = pd.merge(merge, surnames_m_df, on="lastName", suffixes=['_left', '_right'])
    
    merge['lastName'] = merge['lastName'] + '( ' + merge['last_name_m'] + ' )'
    merge = merge.drop('last_name_m', axis=1)
    
    merge_t = merge.set_index("lastName").transpose()
    merge_t = merge_t.reset_index(level=0)
    merge_t = merge_t.rename(columns={"index": "Category"})
    merge_t = merge_t.round(2)
    

    return [merge_t.to_dict('records'), [{"name": i, "id": i}for i in merge_t.columns]]

def sons_pie_chart(source_data):

    data = source_data[["id", "gender", "fatherId", "noOfSons"]]
    data = data[data["fatherId"] != 0]

    new_data = data[~data["id"].isin(data["fatherId"])]
    new_data = new_data[new_data["gender"] == "Male"]
    new_data_list = [[0, len(new_data)]]

    zerosons = pd.DataFrame(new_data_list, columns=["noOfSons", "Counts"])

    data = data[data['gender'] == "Male"]
    noOfSons = data.groupby("fatherId")["id"].count().reset_index()
    noOfSons = noOfSons.rename(columns={"id": f"noOfSons"})
    morethan1sons = noOfSons.groupby("noOfSons").count().reset_index()
    morethan1sons = morethan1sons.rename(columns={"fatherId": f"Counts"})

    final_noOfSons = pd.concat([zerosons, morethan1sons], ignore_index=True)

    figure=px.pie(
                                final_noOfSons,
                                values="Counts",
                                names="noOfSons",
                                # color_discrete_sequence=px.colors.sequential.RdBu,
                                color_discrete_sequence=px.colors.sequential.Plasma,
                                # color_discrete_sequence=px.colors.qualitative.swatches(),
                            )
    figure.update_layout(
                                plot_bgcolor=colors["background"],
                                paper_bgcolor=colors["background"],
                                font_color=colors["text"],
                            )
    figure.update_traces(textinfo="value", textposition="inside")
    return figure

def daughters_pie_chart(source_data):
    data = source_data[["id", "gender", "fatherId", "noOfSons", "noOfDaughters"]]
    data = data[data["fatherId"] != 0]

    new_data = data[~data["id"].isin(data["fatherId"])]
    new_data = new_data[new_data["gender"] == "Female (Daughter)"]
    new_data_list = [[0, len(new_data)]]

    zerosons = pd.DataFrame(new_data_list, columns=["noOfDaughters", "Counts"])

    data = data[data['gender'] == "Female (Daughter)"]
    noOfDaughters = data.groupby("fatherId")["id"].count().reset_index()
    noOfDaughters = noOfDaughters.rename(columns={"id": f"noOfDaughters"})
    morethan1sons = noOfDaughters.groupby(
        "noOfDaughters").count().reset_index()
    morethan1sons = morethan1sons.rename(columns={"fatherId": f"Counts"})

    noOfDaughters = pd.concat([zerosons, morethan1sons], ignore_index=True)

    figure = px.pie(
                                noOfDaughters,
                                values="Counts",
                                names="noOfDaughters",
                                # color_discrete_sequence=px.colors.sequential.RdBu,
                                color_discrete_sequence=px.colors.sequential.Plasma,
                            )
    figure.update_layout(
                                plot_bgcolor=colors["background"],
                                paper_bgcolor=colors["background"],
                                font_color=colors["text"],
                            )
    figure.update_traces(textinfo="value")
    return figure


def living_pie_chart(source_data):
    living = source_data.groupby("livingStatus")["id"].count().reset_index()
    living = living.rename(columns={"id": "Counts"})
        
    figure=px.pie(
                                living,
                                values="Counts",
                                names="livingStatus",
                                # color_discrete_sequence=px.colors.sequential.RdBu,
                                color_discrete_sequence=px.colors.sequential.Plasma,
                            )
    figure.update_layout(
                                plot_bgcolor=colors["background"],
                                paper_bgcolor=colors["background"],
                                font_color=colors["text"],
                            )
    figure.update_traces(textinfo="value")
    return figure

def married_pie_chart(source_data):
    data = source_data[source_data["gender"] == "Male"]
    married = data.groupby("maritalStatus")["id"].count().reset_index()
    married = married.rename(columns={"id": "Counts"})

    figure=px.pie(
                                married,
                                values="Counts",
                                names="maritalStatus",
                                # color_discrete_sequence=px.colors.sequential.RdBu,
                                color_discrete_sequence=px.colors.sequential.Plasma,
                            )
    figure.update_layout(
                                plot_bgcolor=colors["background"],
                                paper_bgcolor=colors["background"],
                                font_color=colors["text"],
                            )
    figure.update_traces(textinfo="value")
    return figure

layout = html.Div(
    children=[
        dcc.Interval(
        id='update-interval',
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
                                    "Analysis on Kulvruttant Data (कुलवृत्तांतातील माहितीचे वर्गीकरण)",
                                    style={
                                        "margin-bottom": "0px",
                                        "textAlign": "center",
                                        "color": colors["text"],
                                    },
                                    id='get_source_data'
                                ),
                            ]
                        )
                    ]
                )
            ]
        ),
    html.Div(
            [
                html.Br(),
                html.Div(
                    id="datatable",
                    children=[
                        dash_table.DataTable(
                            id="summary-datatable1",
                            selected_rows=[],
                            style_header={
                                "backgroundColor": "rgb(30, 30, 30)"},
                            style_cell={
                                "backgroundColor": colors["background"],
                                "color": colors["text"],
                                "text-align": "center",
                                "marginLeft": "auto",
                                "marginRight": "auto",
                                'border': '1px solid gray'
                            },
                            fill_width=False,
                        )
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "align-items": "center",
                    },
                ),
                html.Br(),
                html.Div(id="datatable-row-ids"),
            ]
        ),
    html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns",
                    children=[
                        html.Br(),
                        html.H1(
                            "Number of Sons (पुत्र संख्या)",
                            style={
                                "margin-bottom": "0px",
                                "textAlign": "center",
                                "color": colors["text"],
                            },
                        ),
                        dcc.Graph(
                            id="pie_chart_sons"
                            ),
                    ],
                    id="pie_chart1",
                    style={
                        "backgroundColor": colors["background"],
                    },
                ),
                html.Div(
                    className="six columns",
                    children=[
                        html.Br(),
                        html.H1(
                            "Number of Daughters (कन्या संख्या)",
                            style={
                                "margin-bottom": "0px",
                                "textAlign": "center",
                                "color": colors["text"],
                            },
                        ),
                        dcc.Graph(
                            id="pie_chart_daughters"
                        ),
                    ],
                    id="pie_chart2",
                    style={
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
                        html.Br(),
                        html.H1(
                            "Living Status (जीवित/मृत वर्गीकरण)",
                            style={
                                "margin-bottom": "0px",
                                "textAlign": "center",
                                "color": colors["text"],
                            },
                        ),
                        dcc.Graph(
                            id="pie_chart_living"
                        ),
                    ],
                    id="pie_chart3",
                    style={
                        "backgroundColor": colors["background"],
                    },
                ),
                html.Div(
                    className="six columns",
                    children=[
                        html.Br(),
                        html.H1(
                            "Marital Status (विवाहित/अविवाहित वर्गीकरण)",
                            style={
                                "margin-bottom": "0px",
                                "textAlign": "center",
                                "color": colors["text"],
                            },
                        ),
                        dcc.Graph(
                            id="pie_chart_married"
                        ),
                    ],
                    id="pie_chart4",
                    style={
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

@callback(Output(component_id='summary-datatable1', component_property='data'),
          Output(component_id='summary-datatable1', component_property='columns'),
          Output(component_id='pie_chart_sons', component_property='figure'),
          Output(component_id='pie_chart_daughters', component_property='figure'),
          Output(component_id='pie_chart_living', component_property='figure'),
          Output(component_id='pie_chart_married', component_property='figure'),
          Input('update-interval', 'n_intervals'))

def update_datatable(n_intervals):
    cur.execute(summary_sql)
    source_data = cur.fetchall()
    main_df = pd.DataFrame(source_data, columns=['id','gharaneId','gharane','firstName','lastName','fullName', 'gender','livingStatus','maritalStatus','fatherId','birthDate','deathDate','noOfSons','noOfDaughters'])

    cur.execute(surnames_m)
    surnames_source_data = cur.fetchall()

    surnames_m_df = pd.DataFrame(surnames_source_data, columns=['last_name_m', 'lastName'])

    main_df["birthDate"] = pd.to_datetime(
        main_df["birthDate"], errors="coerce")
    main_df["deathDate"] = pd.to_datetime(
        main_df["deathDate"], errors="coerce")
    
    dt = summary_datatable(main_df, surnames_m_df)

    sons = sons_pie_chart(main_df)
    daughters = daughters_pie_chart(main_df)
    living = living_pie_chart(main_df)
    married = married_pie_chart(main_df)

    return dt[0], dt[1], sons, daughters, living, married