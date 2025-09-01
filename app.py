import dash
from dash import Dash, html, dcc
from mylibrary import *
from myconfig import *

app = Dash(__name__, use_pages=True, title='TI-Monitoring')
server = app.server

def serve_layout():
    layout = [
        html.Header(children = [
            html.Div(id='logo-wrapper', children = [
                html.A(href=home_url, children = [
                    html.Img(id='logo', src='assets/logo.svg')
                ])
            ]),
            html.H1(children='TI-Monitoring')
        ]),
		html.Main(children = [
			html.Div(id='page-container', children=[
                dcc.Loading(
                    id = 'spinner',
                    overlay_style = {"visibility":"visible", "filter": "blur(2px)"},
                    type = "circle",
                    children = [dash.page_container]
                )
            ]),
			html.Div(className = 'box', children = [
                html.H3('Disclaimer'),
                html.Span('Die Bereitstellung der abgebildeten Informationen erfolgt ohne Gewähr. Als Grundlage dienen Daten der gematik GmbH, die sich über eine öffentlich erreichbare Schnittstelle abrufen lassen. Weitere Informationen dazu hier: '),
                html.A('https://github.com/gematik/api-tilage', href='https://github.com/gematik/api-tilage', target='_blank'),
                html.Span('.')
            ]),
		]),
		html.Div(id = 'footer', children = [
            html.Div([html.A('Home', href=home_url, target='_self')]),
            html.Div([html.A('Alerts', href=home_url + '/alerts', target='_self')]),
            html.Div([html.A('Dokumentation', href='https://github.com/lsr-dev/ti-monitoring', target='_blank')]),
            html.Div([html.A('Presse', href='https://heise.de/-10625281', target='_blank')]),
            html.Div([html.A('Datenschutz', href='https://lukas-schmidt-russnak.de/datenschutz/', target='_blank')]),
            html.Div([html.A('Impressum', href='https://lukas-schmidt-russnak.de/impressum/', target='_blank')]),
            html.Div('© Lukas Schmidt-Russnak'),
            html.Iframe(id='ntfy_footer', src=ntfy_url)
        ])
    ]
    return layout

app.layout = serve_layout

if __name__ == '__main__':
    app.run(debug=False)