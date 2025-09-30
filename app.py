from dash import Dash, html, dash_table, dcc, Input, Output, callback
from dash.dash_table.Format import Format, Scheme
import plotly.express as px
from numpy import log10, ones
from pandas import read_csv

# ------------------ GENERATE CONTENT ------------------
# getting data
cat = read_csv('assets/rg_cat_processed.csv')
cat['RmaxEV'] = 10**(cat['Rmax'] - 18)
cat['logFsyn'] = log10(cat['Fsyn'])
cat['logFcr'] = log10(cat['Fcr'])

cat['class'] = cat['class'].replace({'j': 'jetted', 'u': 'unknown', 'g': 'SFG', 'p': 'point src'})

# ------------------------------------------------------
# initialise app
app = Dash(__name__)
app.title = 'Radio Galaxy Catalog'

# add content to app
app.layout = [
    html.Div([
        html.Div([
            html.H1(children='"All-sky catalog of radio-emitting galaxies"'),
            html.P([
                html.Span('Based on the '),
                html.A(children="RG Catalog", href="https://ragolu.science.ru.nl/index.html"),
                html.Span([' from van Velzen et al. (2012) but extended with the inferred cosmic-ray luminosity and maximum rigidity calculated with the framework of Eichmann et al. (2022).']),
                html.Br(),
                html.Span('created by '),
                html.A('D. Ehlert', href='https://domenike.folk.ntnu.no', target='_blank', rel='noopener noreferrer')
            ], style={'width': '70%'}),
        ], className='highlight'),
        # tabl of all radio galaxies with parameters
        html.Div([
            # title and preamble
            html.H2('Catalog Overview'),
            html.Div([
                html.P('Special key:', className='label'),
                html.Ul(id='table-key', children=[
                    html.Li(['F/L', html.Sub('syn'), ': synthetic 1.1GHz flux / luminosity (extrapol. from 843MHz (SUMSS) or 1.4GHz (NVSS))'], className='tight'),
                    html.Li(['P', html.Sub('cav'), ': cavity / jet power calculated as in ', html.A('Matthews et al. 2018', href='https://arxiv.org/abs/1805.01902')], className='tight'),
                    html.Li(['R', html.Sub('max'), ': maximum rigidity inferred from the jet power'], className='tight')
                ])
            ]),
            # the data table itself
            dash_table.DataTable(
                data=cat.to_dict('records'),
                page_size=15,
                columns=[
                    {"name": "Name", "id": "NED_id"},
                    {"name": "Type", "id": "class"},
                    {
                        "name": "RA [°]",
                        "id": "ra",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                    {
                        "name": "Dec [°]",
                        "id": "dec",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                    {
                        "name": "redshift",
                        "id": "zdist",
                        "type": "numeric",
                        "format": Format(precision=3, scheme=Scheme.fixed)
                    },
                    {
                        "name": "D [Mpc]",
                        "id": "D",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                    {
                        "name": "Fsyn [mJy]",
                        "id": "Fsyn",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                    {
                        "name": "log Lsyn [erg/s]",
                        "id": "Lsyn",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                    {
                        "name": "log Pcav [erg/s]",
                        "id": "Pcav",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                    {
                        "name": "log Rmax [eV]",
                        "id": "Rmax",
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    },
                ],
                style_as_list_view=True,
                fill_width=False,
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'maxWidth': '7em',
                },
                style_cell={
                    'padding': '7px',
                    'height': 'auto',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': '10em',
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['NED_id', 'class']
                ],
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in cat.to_dict('records')
                ],
                tooltip_duration=None,
            ),
        ], style={'width': '70%'}),
        html.H2('Distance-Distribution of Sources'),
        dcc.RadioItems(
            options=['All', 'Jetted', 'Unknown', 'SFG', 'Point Source'],
            value='All',
            id='class-button',
            className="button two columns",
            style={'marginTop': '4vh'}),
        html.Div([
            dcc.Graph(id='histogram-fig', style={"width": "100%", "height": "600px"})], className="ten columns"),
        html.H2('Source Luminosity / Flux / Maximum Rigidity'),
        html.Div([
            html.Label(
                'x Scale',
                className="label",
                style={'marginTop': '4vh'}),
            html.Br(),
            dcc.RadioItems(
                options=[
                    {
                        'label': 'lin',
                        'value': False
                    },
                    {
                        'label': 'log',
                        'value': True
                    },
                ],
                value=True,
                id='scatterplot-xscale-button',
                className="button",
                style={'marginTop': '0.3vh'}),
            html.Br(),
            html.Label(
                'y Axis',
                className="label",
                style={'marginTop': '2vh'}),
            html.Br(),
            dcc.RadioItems(
                options=[
                    {
                        'label': [html.Span("P"), html.Sub("cav")],
                        'value': 'Pcav'
                    },
                    {
                        'label': [html.Span("L"), html.Sub("syn")],
                        'value': 'Lsyn'
                    },
                    {
                        'label': [html.Span("L"), html.Sub("CR")],
                        'value': 'Lcr'
                    },
                    {
                        'label': [html.Span("F"), html.Sub("syn")],
                        'value': 'logFcr'
                    },
                    {
                        'label': [html.Span("F"), html.Sub("CR")],
                        'value': 'logFcr'
                    },
                    {
                        'label': [html.Span("R"), html.Sub("max")],
                        'value': 'Rmax'
                    },
                ],
                value='Pcav',
                id='scatterplot-yaxis-button',
                className="button",
                style={'marginTop': '0.3vh'}),
            html.Label(
                'Object Type',
                className="label",
                style={'marginTop': '2vh'}),
            html.Br(),
            dcc.Slider(
                min=0, max=4, step=1, value=3,
                vertical=True,
                verticalHeight=250,
                id="scatterplot-class-slider",
                marks={
                    4: "All",
                    3: "Jetted",
                    2: "Unknown",
                    1: "SFG",
                    0: "Point Source"
                },
                included=False,
                updatemode='drag',
                className="slider")
        ], className="two columns"),
        html.Div([
            dcc.Graph(id='scatterplot-fig', style={"width": "100%", "height": "850px"})], className="ten columns"),
    ], style={'padding': '2vw'}),
]


@callback(
    Output('histogram-fig', 'figure'),
    Input('class-button', 'value'))
def update_histogram(class_label):
    color_dict = {'Jetted': '#636EFA', 'Unknown': '#EF553B', 'SFG': '#00CC96', 'Point Source': '#AB63FA'}
    if class_label == 'All':
        fig = px.histogram(cat, x='D', color='class', template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    else:
        mask_class = cat['class'] == str.lower(class_label).replace('sfg', 'SFG').replace('point source', 'point src')
        fig = px.histogram(cat[mask_class], x='D', color_discrete_sequence=[color_dict[class_label]], template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    return fig


@callback(
    Output('scatterplot-fig', 'figure'),
    Input('scatterplot-yaxis-button', 'value'),
    Input('scatterplot-class-slider', 'value'),
    Input('scatterplot-xscale-button', 'value'))
def update_scatterplot(yaxis_parameter, class_value, x_scale):
    # mask = (cat['D'] <= 500)
    class_dict = {4: 'all', 3: 'jetted', 2: 'unknown', 1: 'SFG', 0: 'point src'}
    class_label = class_dict[class_value]
    if class_label == 'all':
        mask_class = ones(len(cat), dtype=bool)
    else:
        mask_class = (cat['class'] == class_label)
    fig = px.scatter(cat[mask_class], x='D', y=yaxis_parameter, color='Lsyn', color_continuous_scale='plasma', template='plotly_white', size='RmaxEV', custom_data={'NED_id': True, 'Lsyn': True, 'Lcr': True, 'Rmax': True}, log_x=x_scale, labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'Pcav': 'log <i>P</i><sub>cav</sub> [erg / s]', 'Lsyn': 'log <i>L</i><sub>syn</sub> [erg / s]', 'Lcr': 'log <i>L</i><sub>CR</sub> [erg / s]', 'Rmax': 'log <i>R</i><sub>max</sub> [eV]', 'logFsyn': 'log <i>F</i><sub>syn</sub> [erg / s / cm<sup>2</sup>]', 'logFcr': 'log <i>F</i><sub>CR</sub> [erg / s / cm<sup>2</sup>]'})
    fig.update_traces(marker_sizemin=4,
                      selector=dict(type='scatter'),
                      hovertemplate=("<b>%{customdata[0]}</b><br>" + "<i>D</i><sub>lumi</sub> [Mpc] = %{x:.2f}<br>" +
                                     "log <i>P</i><sub>cav</sub> [erg / s] = %{y:.2f}<br>" +
                                     "log <i>L</i><sub>syn</sub> [erg / s] = %{customdata[1]:.2f}<br>" +
                                     "log <i>L</i><sub>CR</sub> [erg / s] = %{customdata[2]:.2f}<br>" +
                                     "log <i>R</i><sub>max</sub> [eV] = %{customdata[3]:.2f}"))
    fig.update_layout(coloraxis_colorbar=dict(orientation='h', title_side='right'))
    return fig


if __name__ == '__main__':
    # Bind to 0.0.0.0 so the container can receive external traffic
    app.run_server(host="0.0.0.0", port=8080, debug=False)
