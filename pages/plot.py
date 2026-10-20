import dash
from dash import html, dcc, Input, Output
import plotly.express as px

from mylibrary import *
from myconfig import *


dash.register_page(__name__)


def get_plot_data(ci, period):
    ci_data = get_availability_data_of_ci(
        file_name,
        ci,
    )

    if period == "recent":
        cutoff = (
            pd.Timestamp.now(
                tz=get_localzone()
            )
            - pd.Timedelta(
                hours=stats_delta_hours
            )
        )

        ci_data = ci_data[
            ci_data["times"] >= cutoff
        ]

    return ci_data


def create_statistics(ci_data):
    if len(ci_data["values"]) == 0:
        return html.Div(
            className="box",
            children=[
                html.H3("Statistik"),
                html.P(
                    "Keine Daten für diesen Zeitraum vorhanden."
                ),
            ],
        )

    number_of_values = len(
        ci_data["values"]
    )

    mean_availability = np.mean(
        ci_data["values"].values
    )

    first_timestamp = (
        ci_data["times"]
        .iloc[0]
        .strftime(
            "%d.%m.%Y %H:%M:%S Uhr"
        )
    )

    last_timestamp = (
        ci_data["times"]
        .iloc[-1]
        .strftime(
            "%d.%m.%Y %H:%M:%S Uhr"
        )
    )

    return html.Div(
        id="statistics",
        className="box",
        children=[
            html.H3("Statistik"),
            html.Ul(
                [
                    html.Li(
                        "Anzahl der Werte: "
                        + str(number_of_values)
                    ),
                    html.Li(
                        "Erster Wert: "
                        + first_timestamp
                    ),
                    html.Li(
                        "Letzter Wert: "
                        + last_timestamp
                    ),
                    html.Li(
                        "Verfügbarkeit in diesem Zeitraum: "
                        + str(
                            mean_availability * 100
                        )
                        + " %",
                    ),
                ]
            ),
        ],
    )


def create_graph(ci_data):
    if len(ci_data["values"]) == 0:
        return dcc.Graph(
            figure=px.scatter(
                title="Keine Daten vorhanden"
            )
        )

    ci_data = ci_data.rename(
        columns={
            "times": "Zeit",
            "values": "Verfügbarkeit",
        }
    )

    custom_colors = [
        "red" if value == 0 else "green"
        for value in ci_data["Verfügbarkeit"]
    ]

    fig = px.scatter(
        ci_data,
        x="Zeit",
        y="Verfügbarkeit",
    )

    fig.update_traces(
        marker=dict(
            color=custom_colors
        )
    )

    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=["0", "1"],
    )

    fig.update_layout(
        yaxis=dict(
            range=[-0.1, 1.1]
        )
    )

    return dcc.Graph(
        figure=fig
    )


def serve_layout(
    ci=None,
    **other_unknown_query_strings
):
    ci_info = get_data_of_ci(
        file_name,
        ci,
    )

    return [
        dcc.Store(
            id="plot-ci",
            data=ci,
        ),

        html.H2(
            "Verfügbarkeit der Komponente "
            + str(ci)
        ),

        html.H3(
            ci_info["product"]
            + ", "
            + ci_info["name"]
            + ", "
            + ci_info["organization"]
        ),

        html.A(
            href=home_url,
            className="plot-back-button",
            children=[
                html.Button(
                    "Zurück",
                    className="button",
                )
            ],
        ),

        dcc.Tabs(
            id="plot-period",
            value="recent",
            children=[
                dcc.Tab(
                    label=(
                        "Letzte "
                        + str(stats_delta_hours)
                        + " Stunden"
                    ),
                    value="recent",
                ),
                dcc.Tab(
                    label="Alle Daten",
                    value="all",
                ),
            ],
        ),

        html.Div(
            id="plot-period-info"
        ),

        html.Div(
            id="plot-statistics"
        ),

        html.Div(
            id="plot-graph"
        ),
    ]


@dash.callback(
    Output(
        "plot-statistics",
        "children",
    ),
    Output(
        "plot-graph",
        "children",
    ),
    Output(
        "plot-period-info",
        "children",
    ),
    Input(
        "plot-period",
        "value",
    ),
    Input(
        "plot-ci",
        "data",
    ),
)
def update_plot(
    period,
    ci,
):
    ci_data = get_plot_data(
        ci,
        period,
    )

    statistics = create_statistics(
        ci_data
    )

    graph = create_graph(
        ci_data
    )

    period_info = html.Div(
        className="plot-period-info",
        children=[
            "Hinweis: ..."
        ],
    )

    return (
        statistics,
        graph,
        period_info,
    )


layout = serve_layout
