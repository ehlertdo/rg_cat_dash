from dash import Dash, html, dash_table, dcc, Input, Output, callback
from dash.dash_table.Format import Format, Scheme
import plotly.express as px
import pandas as pd

# ------------------ GENERATE CONTENT ------------------
# getting data
cat = pd.read_csv('assets/rg_cat_processed.csv')
mask = (cat['D'] <= 500)
mask_class = (cat['class'] == 'j')
cat['RmaxEV'] = 10**(cat['Rmax'] - 18)

# fig = px.scatter(cat[mask * mask_class], x='D', y='Pcav', color='Lsyn', color_continuous_scale='plasma', template='plotly_white', size_max=20, size='RmaxEV', hover_data={'NED_id': True, 'Lsyn': True, 'Rmax': True}, log_x=True, range_y=[41.5, 47], height=600, labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'Pcav': 'log <i>P</i><sub>cav</sub> [erg / s]', 'Lsyn': 'log <i>L</i><sub>syn</sub> [erg / s]'})
# fig.update_traces(marker_sizemin=3,
#                   selector=dict(type='scatter'),
#                   hovertemplate=("<b>%{customdata[0]}</b><br>" + "<i>D</i><sub>lumi</sub> [Mpc] = %{x:.2f}<br>" +
#                                  "log <i>P</i><sub>cav</sub> [erg / s] = %{y:.2f}<br>" +
#                                  "log <i>L</i><sub>syn</sub> [erg / s] = %{customdata[1]:.2f}<br>" +
#                                  "log <i>R</i><sub>max</sub> [eV] = %{customdata[2]:.2f}"))
# fig.update_layout(coloraxis_colorbar=dict(orientation='h', title_side='right'))

cat['class'] = cat['class'].replace({'j': 'jetted', 'u': 'unknown', 'g': 'SFG', 'p': 'point src'})


# fig2 = px.histogram(cat, x='D', color='class', template='plotly_white', marginal="rug", height=600, labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
# ------------------------------------------------------
# [['NED_id', 'class', 'zdist', 'D', 'Fsyn', 'Lsyn', 'Rmax']]
# initialise app
app = Dash(__name__)
app.title ='Radio Galaxy Catalog'
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
                html.Br(),
                html.Span('created by '),
                html.A('D. Ehlert', href='https://domenike.folk.ntnu.no', target='_blank', rel='noopener noreferrer')
            ], style={'width': '70%'}),
        ], style={'fontWeight': 'bold', 'color': 'darkslategrey'}),
        html.H2('Catalog Overview'),
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
                    "format": Format(precision=2, scheme=Scheme.fixed)
                },
                {
                    "name": "D [Mpc]",
                    "id": "D",
                    "type": "numeric",
                    "format": Format(precision=2, scheme=Scheme.fixed)
                },
                {
                    "name": "log Fsyn [mJy]",
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
        html.H2('Distance-Distribution of Sources'),
        dcc.RadioItems(
            options=['All', 'Jetted', 'Unknown', 'SFG', 'Point Source'],
            value='All',
            id='class-button',
            className="button two columns",
            style={'marginTop': '4vh'}),
        html.Div([
            dcc.Graph(id='histogram-fig', style={"width": "100%", "height": "40vh"})], className="ten columns"),
        html.H2('Source Luminosity / Power / Maximum Rigidity'),
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
                    'label': [html.Span("R"), html.Sub("max")],
                    'value': 'Rmax'
                },
            ],
            value='Pcav',
            id='scatterplot-button',
            className="button two columns",
            style={'marginTop': '4vh'}),
        html.Div([
            dcc.Graph(id='scatterplot-fig', style={"width": "100%", "height": "60vh"})], className="ten columns"),
    ], style={'padding': '2vw'}),
]


@callback(
    Output('histogram-fig', 'figure'),
    Input('class-button', 'value'))
def update_histogram(class_value):
    if class_value == 'All':
        fig = px.histogram(cat, x='D', color='class', template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    elif class_value == 'Jetted':
        fig = px.histogram(cat[cat['class'] == 'jetted'], x='D', color_discrete_sequence=['#636EFA'], template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    elif class_value == 'Unknown':
        fig = px.histogram(cat[cat['class'] == 'unknown'], x='D', color_discrete_sequence=['#EF553B'], template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    elif class_value == 'SFG':
        fig = px.histogram(cat[cat['class'] == 'SFG'], x='D', color_discrete_sequence=['#00CC96'], template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    elif class_value == 'Point Source':
        fig = px.histogram(cat[cat['class'] == 'point src'], x='D', color_discrete_sequence=['#AB63FA'], template='plotly_white', marginal="rug", labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'class': 'Object Type'})
    return fig


@callback(
    Output('scatterplot-fig', 'figure'),
    Input('scatterplot-button', 'value'))
def update_scatterplot(yaxis_parameter):
    fig = px.scatter(cat[mask * mask_class], x='D', y=yaxis_parameter, color='Lsyn', color_continuous_scale='plasma', template='plotly_white', size_max=20, size='RmaxEV', custom_data={'NED_id': True, 'Lsyn': True, 'Lcr': True, 'Rmax': True}, log_x=True, labels={'D': '<i>D</i><sub>lumi</sub> [Mpc]', 'Pcav': 'log <i>P</i><sub>cav</sub> [erg / s]', 'Lsyn': 'log <i>L</i><sub>syn</sub> [erg / s]', 'Lcr': 'log <i>L</i><sub>CR</sub> [erg / s]', 'Rmax': 'log <i>R</i><sub>max</sub> [eV]'})
    fig.update_traces(marker_sizemin=3,
                      selector=dict(type='scatter'),
                      hovertemplate=("<b>%{customdata[0]}</b><br>" + "<i>D</i><sub>lumi</sub> [Mpc] = %{x:.2f}<br>" +
                                     "log <i>P</i><sub>cav</sub> [erg / s] = %{y:.2f}<br>" +
                                     "log <i>L</i><sub>syn</sub> [erg / s] = %{customdata[1]:.2f}<br>" +
                                     "log <i>L</i><sub>CR</sub> [erg / s] = %{customdata[2]:.2f}<br>" +
                                     "log <i>R</i><sub>max</sub> [eV] = %{customdata[3]:.2f}"))
    fig.update_layout(coloraxis_colorbar=dict(orientation='h', title_side='right'))
    return fig


if __name__ == '__main__':
    app.run(debug=True)
