import dash
from dash import html, dcc
import plotly.express as px
from mylibrary import *
from myconfig import *

dash.register_page(__name__)

def serve_layout():
    layout = [
        html.H2('Push-Benachrichtigungen'),
        html.P('Sie können sich per Push-Nachricht über Änderungen des Verfügbarkeitsstatus benachrichtigen lassen. Wichtig: Die hier angebotenen Push-Nachrichten basieren auf einem generischen Benachrichtigungsprofil, d.h. es werden Benachrichtigungen zu allen Komponenten versendet'),
        html.H3('Option 1 (empfohlen)'),
        html.P(
            children = [
                html.Span('Laden Sie hierzu die App „ntfy“ aus dem App Store herunter ('),
                html.A('Apple App Store', href='https://apps.apple.com/de/app/ntfy/id1625396347'),
                html.Span(', '),
                html.A('Google Play Store', href='https://play.google.com/store/apps/details?id=io.heckel.ntfy'),
                html.Span(') und richten Sie diese wie folgt ein:')
            ]
        ),
        html.Ol(
            children = [
                html.Li('Akzeptieren Sie, dass die App Ihnen Mitteilungen sendet, falls danach gefragt wird.'),
                html.Li('Klicken Sie auf das  „+“, um eine neue Subscription hinzuzufügen.'),
                html.Li('Geben Sie als topic „TI“ ein.'),
                html.Li('Aktivieren Sie die Option „Use another server“ und geben Sie als Service URL „https://push.ti-monitoring.de“ ein.'),
                html.Li('Tippen Sie auf „Subscribe“.')
            ]
        ),
        html.H3('Option 2'),
        html.P(
            children = [
                html.P('Alternativ können Sie sich auf Ihrem Deskop-Gerät über Ihren Browser beanchrichtigen lassen. Rufen Sie hierzu die folgende Seite auf und erlauben Sie Ihrem Browser, Desktop-Benachrichtigungen anzuzeigen: '),
                html.A('Benachrichtigungen im Browser', href='https://push.ti-monitoring.de/TI', target="_self"),
                html.P('Anschließend können Sie auf die Seiten des TI-Monitorings zurückkehren.')
            ]
        )
    ]
    return layout

layout = serve_layout