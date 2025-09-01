import dash
from dash import html
from mylibrary import *
from myconfig import *

dash.register_page(__name__, path='/')

def serve_layout():
    cis = get_data_of_all_cis(file_name)
    grouped = cis.groupby('product')
    products = []
    for index, row in cis.iterrows():
        product = row['product']
        if product not in products:
            products.append(product)
    layout = html.Div([
        html.P('Hier finden Sie eine nach Produkten gruppierte Übersicht zentraler Komponenten der Telematikinfrastruktur (TI). Neue Daten werden alle 5 Minuten bereitgestellt. Laden Sie die Seite neu, um die Ansicht zu aktualisieren.'),
        html.Div(className='accordion', children = [
            html.Div(className='accordion-element', children = [
                html.Div(
                    className='accordion-element-title',
                    children = [
                        html.Span(className = 'availability-icon ' + 
                            'available' if sum(group['current_availability']) == len(group)
                            else 'availability-icon unavailable' if sum(group['current_availability']) == 0
                            else 'availability-icon impaired',
                        ),
                        html.Span(
                            className = 'group-name',
                            children = group_name + ' (' + str(sum(group['current_availability'] == 1)) + '/' + str(len(group)) + ')'
                        ),
                        html.Span(className = 'expand-collapse-icon', children='+')
                    ]
                ),
                html.Div(className='accordion-element-content', children = [
                    html.Ul(children = [
                        html.Li([
                            html.Span(className = 'availability-icon ' + 'available' if row['current_availability'] == 1 else 'availability-icon unavailable'),
                            html.Div([
                                html.A(str(row['ci']), href='/plot?ci=' + str(row['ci'])),
                                ': ' + row['name'] + ', ' + row['organization'] + ', ' + pretty_timestamp(row['time'])
                            ])
                        ]) for _, row in group.iterrows()
                    ])
                ])
            ]) for group_name, group in grouped
        ])
    ])
    return layout

layout = serve_layout