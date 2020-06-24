# -*- coding: utf-8 -*-

# - Pryno Dashboard Frontend -
# 🦏 *** quan.digital *** 🦏

# authors: canokaue & claudiovb
# date: 05/2020
# kaue.cano@quan.digital

# Bot monitoring dashboard developed using Plot.ly Dash
# Originally developed for Quan Digital's Pryno project - https://github.com/quan-digital/Pryno
# Code based on stock Plot.ly's Dash Oil and Gas example - https://dash-gallery.plotly.host/dash-oil-and-gas/
# Dash documentation - https://dash.plotly.com/

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pryno.util.tools as tools
import pryno.util.settings as settings

clients_dash = html.Div(
    [
        dcc.Store(id='aggregate_data'),

        # Header
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            'Pryno Beta Dashboard: {0}'.format(
                                settings.STRATEGY_NAME),
                            style={'padding-left': '65px',
                                   'padding-top': '20px'}

                        ),
                        html.H5(
                            'Account: {0}'.format(settings.CLIENT_NAME),
                            style={'padding-left': '65px',
                                   'font-size': '1.5rem'}
                        ),
                        html.H5(
                            id='status',
                            style={'padding-left': '65px',
                                   'font-size': '1.5rem'}
                        ),
                        html.H5(
                            id='timestamp',
                            style={'padding-left': '65px',
                                   'font-size': '1.5rem'}
                        ),
                    ],

                    className='eight columns'
                ),
                dcc.ConfirmDialogProvider(
                    children=html.A(
                        html.Button(
                            html.H5(

                                id='button_name',
                                className="info_text",
                                style={'padding-left': '0px',
                                       'font-size': '1.0rem'}
                            ),
                            id="pause_button"
                        ),
                        className="two columns"

                    ),
                    message="Press 'OK' to run bot, and 'Cancel' to pause operation",
                    id='pause_confirm'
                ),
                html.Div(id='pause_message',
                         children="",
                         style={'text-align': 'center'}),
                html.Img(
                    src="assets/logo-light.png",
                    className='two columns',
                    style={'align': 'left'}
                ),
                html.A(
                    html.Button(
                        "Learn More",
                        id="learnMore"
                    ),
                    href="https://quan.digital",
                    className="two columns"
                )
            ],
            id="header",
            className='row',
        ),

        # Upper page components
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P("Open Orders"),
                                html.H6(
                                    className="info_text",
                                    id="open_orders",
                                    style={'whiteSpace': 'pre-wrap'}
                                )
                            ],
                            className="pretty_container"
                        ),
                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        # First info row
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("Profit"),
                                        html.H6(
                                            id="profit",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Order Num"),
                                        html.H6(
                                            id="order_num",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Position"),
                                        html.H6(
                                            id="position",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Stop"),
                                        html.H6(
                                            id="stop",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Liquidation"),
                                        html.H6(
                                            id="liquidation",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Break Even"),
                                        html.H6(
                                            id="beven",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                            ],
                            id="btcInfo",
                            className="row"
                        ),

                        # Second info row
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("Price"),
                                        html.H6(
                                            id="btc",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P(
                                            id="html_p1",
                                            className="info_text"),
                                        html.H6(
                                            id="volume",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P(
                                            id="html_p2",
                                            className="info_text"),
                                        html.H6(
                                            id="amplitude",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P(id="html_p3",
                                               className="info_text"),
                                        html.H6(
                                            id="dolmin",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P(id="html_p4",
                                               className="info_text"),
                                        html.H6(
                                            id="lockAnom",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Funds"),
                                        html.H6(
                                            id="funds",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                                html.Div(
                                    [
                                        html.P("Margin"),
                                        html.H6(
                                            id="margin",
                                            className="info_text"
                                        )
                                    ],
                                    id="",
                                    className="pretty_container"
                                ),

                            ],
                            id="infoContainer",
                            className="row"
                        ),

                        # Profit overtime plot
                        html.Div(
                            [
                                html.P("BTC Price @ Bitmex"),
                                dcc.Graph(
                                    figure={
                                        'layout': go.Layout(
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            plot_bgcolor='rgba(0,0,0,0)'
                                        )},
                                    id='count_graph',
                                )
                            ],
                            id="countGraphContainer",
                            className="pretty_container",
                            style=dict(minHeight="250px")
                        )
                    ],
                    id="rightCol",
                    className="eight columns"
                )
            ],
            id='upper_info',
            className="row"
        ),


        # Bottom components (executions and errors)
        html.Div(
            [
                html.Div(
                    [
                        html.P("Executions"),
                        html.H6(
                            id="executions",
                            className="info_text",
                            style={'whiteSpace': 'pre-wrap'}
                        )
                    ],
                    id="",
                    className="pretty_container",
                    style=dict(overflow="scroll", maxHeight="550px")

                ),
                html.Div(
                    [
                        html.P(
                            id="html_p5",
                            className="info_text",
                            style={'whiteSpace': 'pre-wrap'}),
                        html.H6(
                            id="errors",
                            className="info_text",
                            style={'whiteSpace': 'pre-wrap'}
                        )
                    ],
                    id="",
                    className="pretty_container",
                    style=dict(overflow="scroll", maxHeight="550px")
                ),
            ],
            id='lower_info',
            className='row'
        ),

        # Footer
        html.Div(
            [
                html.P(
                    'Designed by canokaue & claudiovb',
                    style={
                        #                          'padding-left':'65px',
                        'font-size': '1.5rem',
                        'color': '#b5c6cc',
                        'align': 'left',
                    }
                ),

                html.P(
                    'Pryno Dashboard <b>BETA v {0}</b> - © Quan Digital 2020'.format(
                        settings.BOT_VERSION),
                    style={
                        'padding-left': '165px',
                        'font-size': '1.5rem',
                        'color': '#b5c6cc',
                        'align': 'left',
                    }
                ),
            ],
            id='footer',
            className="row"
        ),

        # Update loop component
        dcc.Interval(
            id='interval-component',
            interval=settings.DASH_INTERVAL * 1000,
            n_intervals=0
        )
    ],
    id="teste",
    style={
        "display": "flex",
        "flex-direction": "column"
    },
)
