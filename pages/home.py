import pandas as pd
import dash

from datetime import datetime
from zoneinfo import ZoneInfo

from dash import (
    html,
    dcc,
    Input,
    Output,
    callback,
)

from mylibrary import (
    pretty_timestamp,
    read_data_cache,
)


dash.register_page(
    __name__,
    path="/",
)


# =========================================================
# CONFIGURATION
# =========================================================

# Refresh the displayed data every 30 seconds.
#
# This does NOT:
#   - reload the browser page
#   - call an API
#   - read the HDF5 file
#
# It only triggers the Dash callback, which reads
# data_cache.json.
#
REFRESH_INTERVAL = 30 * 1000


# =========================================================
# TI APPLICATIONS
# =========================================================

SERVICE_NAMES = {
    "epa": "ePA",
    "vsdm": "VSDM",
    "erezept": "E-Rezept",
    "kim": "KIM",
    "wanda": "WANDA",
    "ogd": "ÖGD",
    "tianschluss": "TI-Anschluss",
}


SERVICE_DESCRIPTIONS = {
    "epa": "elektronische Patientenakte",
    "vsdm": "Versichertenstammdatenmanagement",
    "erezept": "elektronisches Rezept",
    "kim": "Kommunikation im Medizinwesen",
    "wanda": "Weitere Anwendungen für den Datenaustausch",
    "ogd": "Öffentliches Gesundheitswesen",
    "tianschluss": "Anschluss an die Telematikinfrastruktur",
}


def create_status_card(
    service_name,
    service_description,
    status_text,
    status_class,
):
    """
    Create a dashboard card for one TI application.

    The title attribute is attached to the complete card,
    so the browser tooltip is shown when hovering anywhere
    over the card.
    """

    return html.Div(
        [
            html.H2(
                service_name,
                className="status-card-title",
            ),

            html.Div(
                status_text,
                className=(
                    f"status-card-value {status_class}"
                ),
            ),
        ],
        className=f"status-card {status_class}",
        title=service_description,
    )


def create_app_status(cache):
    """
    Build the TI application status section
    from the server-side cache.

    This function NEVER calls the TI API
    and NEVER reads the HDF5 file.
    """

    data = cache.get(
        "app_status",
        {},
    )

    if not data:
        return (
            html.Div(
                "Warte auf aktuelle Statusdaten...",
                className="loading",
            ),
            "",
        )

    services = data.get(
        "appStatus",
        {},
    )

    cards = []

    for service_id, service_name in SERVICE_NAMES.items():

        service = services.get(
            service_id,
            {},
        )

        outage = service.get(
            "outage",
            "unknown",
        )

        if outage == "none":
            status_class = "status-ok"
            status_text = "OK"

        elif outage == "full":
            status_class = "status-full"
            status_text = "TOTAL\u00adAUSFALL"

        elif outage == "partial":
            status_class = "status-partial"
            status_text = "TEIL\u00adSTÖRUNG"

        else:
            status_class = "status-unknown"
            status_text = "UNBEKANNT"

        service_description = (
            SERVICE_DESCRIPTIONS.get(
                service_id,
                service_name,
            )
        )

        cards.append(
            create_status_card(
                service_name,
                service_description,
                status_text,
                status_class,
            )
        )

    # -----------------------------------------------------
    # API timestamp
    # -----------------------------------------------------

    timestamp = data.get(
        "timestamp"
    )

    if timestamp:

        try:

            update_time = (
                datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )
                .astimezone(
                    ZoneInfo("Europe/Berlin")
                )
                .strftime(
                    "%d.%m.%Y %H:%M:%S Uhr"
                )
            )

            last_update_text = (
                f"Stand: {update_time}"
            )

        except (
            ValueError,
            TypeError,
        ):

            last_update_text = (
                f"Stand: {timestamp}"
            )

    else:

        last_update_text = (
            "Stand: unbekannt"
        )

    return (
        cards,
        html.Div(
            [
                html.Div(
                    last_update_text,
                    className=(
                        "last-update-timestamp"
                    ),
                ),
            ],
            className="last-update",
        ),
    )


# =========================================================
# CIS MONITORING
# =========================================================

def create_cis_content(cache):
    """
    Build the CIS monitoring accordion
    from the server-side cache.

    This function NEVER reads the HDF5 file.
    """

    data = cache.get(
        "cis",
        [],
    )

    if not data:
        return html.Div(
            "Keine Monitoring-Daten verfügbar."
        )

    cis = pd.DataFrame(data)

    if cis.empty:
        return html.Div(
            "Keine Monitoring-Daten verfügbar."
        )

    # -----------------------------------------------------
    # Sort by product
    # -----------------------------------------------------

    cis = cis.sort_values(
        by="product",
        key=lambda col: col.str.lower(),
    )

    # -----------------------------------------------------
    # Group by product
    # -----------------------------------------------------

    grouped = cis.groupby(
        "product",
        sort=False,
    )

    # -----------------------------------------------------
    # Build accordion
    # -----------------------------------------------------

    return html.Div(
        className="accordion",

        children=[

            html.Div(
                className="accordion-element",

                children=[

                    html.Div(
                        className=(
                            "accordion-element-title"
                        ),

                        children=[

                            html.Span(
                                className=(
                                    "availability-icon "
                                    +
                                    (
                                        "available"
                                        if sum(
                                            group[
                                                "current_availability"
                                            ]
                                        ) == len(group)

                                        else
                                        "unavailable"
                                        if sum(
                                            group[
                                                "current_availability"
                                            ]
                                        ) == 0

                                        else
                                        "impaired"
                                    )
                                ),
                            ),

                            html.Span(
                                className="group-name",
                                children=(
                                    group_name
                                    + " ("
                                    + str(
                                        sum(
                                            group[
                                                "current_availability"
                                            ] == 1
                                        )
                                    )
                                    + "/"
                                    + str(
                                        len(group)
                                    )
                                    + ")"
                                ),
                            ),

                            html.Span(
                                className=(
                                    "expand-collapse-icon"
                                ),
                                children="+",
                            ),
                        ],
                    ),

                    html.Div(
                        className=(
                            "accordion-element-content"
                        ),

                        children=[

                            html.Ul(
                                children=[

                                    html.Li(
                                        [

                                            html.Span(
                                                className=(
                                                    "availability-icon "
                                                    +
                                                    (
                                                        "available"
                                                        if row[
                                                            "current_availability"
                                                        ] == 1
                                                        else
                                                        "unavailable"
                                                    )
                                                ),
                                            ),

                                            html.Div(
                                                [

                                                    html.A(
                                                        str(
                                                            row[
                                                                "ci"
                                                            ]
                                                        ),

                                                        href=(
                                                            "/plot?ci="
                                                            + str(
                                                                row[
                                                                    "ci"
                                                                ]
                                                            )
                                                        ),
                                                    ),

                                                    ": "
                                                    + str(
                                                        row[
                                                            "name"
                                                        ]
                                                    )

                                                    + ", "

                                                    + str(
                                                        row[
                                                            "organization"
                                                        ]
                                                    )

                                                    + ", "

                                                    + pretty_timestamp(
                                                        row[
                                                            "time"
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )

                                    for _, row
                                    in group.iterrows()
                                ]
                            )
                        ],
                    ),
                ]
            )

            for group_name, group
            in grouped
        ],
    )


# =========================================================
# PAGE LAYOUT
# =========================================================

layout = html.Div(
    [

        # -------------------------------------------------
        # Introduction
        # -------------------------------------------------

        html.P(
            "Hier finden Sie eine Übersicht des "
            "aktuellen Status der Anwendungen sowie "
            "zentraler Komponenten der "
            "Telematikinfrastruktur (TI). "
            "Neue Daten werden alle 5 Minuten "
            "bereitgestellt. Die Ansicht wird "
            "automatisch aktualisiert."
        ),


        # -------------------------------------------------
        # TI Applications
        # -------------------------------------------------

        html.H2(
            "Status der TI-Anwendungen"
        ),

        html.Div(
            id="app-status-container",
            className="status-container",
        ),

        html.Div(
            id="app-status-update",
            className="last-update",
        ),


        # -------------------------------------------------
        # CIS Monitoring
        # -------------------------------------------------

        html.H2(
            "Zentrale TI-Komponenten"
        ),

        html.Div(
            id="home-content",
        ),


        # -------------------------------------------------
        # Automatic refresh
        # -------------------------------------------------

        dcc.Interval(
            id="home-refresh",
            interval=REFRESH_INTERVAL,
            n_intervals=0,
        ),
    ]
)


# =========================================================
# AUTOMATIC REFRESH CALLBACK
# =========================================================

@callback(
    Output(
        "app-status-container",
        "children",
    ),

    Output(
        "app-status-update",
        "children",
    ),

    Output(
        "home-content",
        "children",
    ),

    Input(
        "home-refresh",
        "n_intervals",
    ),
)
def refresh_home(_):
    """
    Refresh the complete home page.

    Data flow:

        browser
            ↓
        Dash callback
            ↓
        read_data_cache()
            ↓
        data_cache.json
            ├── app_status
            └── cis

    There is NO API access here.
    There is NO HDF5 access here.
    """

    # Read the cache exactly once per refresh.
    cache = read_data_cache()

    app_status_content, app_status_update = (
        create_app_status(
            cache
        )
    )

    cis_content = create_cis_content(
        cache
    )

    return (
        app_status_content,
        app_status_update,
        cis_content,
    )