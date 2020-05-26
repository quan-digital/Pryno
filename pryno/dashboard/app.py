# -*- coding: utf-8 -*-

# - Pryno Dashboard Backend -
# 🦏 *** quan.digital *** 🦏

# authors: canokaue & claudiovb
# date: 05/2020
# kaue.cano@quan.digital

# Bot monitoring dashboard developed using Plot.ly Dash
# Originally developed for Quan Digital's Pryno project - https://github.com/quan-digital/Pryno
# Dash documentation - https://dash.plotly.com/

import os
import copy
import datetime as dt
import json
import csv
import schedule
import requests
import logging
import flask
from flask_login import user_logged_in
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_auth
import pryno.util.tools as tools
import pryno.util.settings as settings
from pryno.dashboard import client_dash

# This makes the app silent on console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Needed for single main.py file
THREADED_RUN = True

# Make 80 for AWS EC2, default is 5000
PORT = 80

# Make 0.0.0.0 to IP redirect, default is 127.0.0.1
HOST = '0.0.0.0'

# Creating webapp
app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(
    app,
    settings.VALID_USERNAME_PASSWORD_PAIRS
)
server = app.server

# Datetime update
today = dt.datetime.today().strftime('%Y-%m-%d')
def update_today():
    today = dt.datetime.today().strftime('%Y-%m-%d')
    return 
schedule.every(120).seconds.do(update_today)

# Base layout
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Pryno Dashboard',
)

# Create app layout
app.layout = client_dash.clients_dash

# -----------------------------------------------------------------------------------------
# ----------------------Data Load Functions------------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

def load_exec():
    '''Load list of executions from csv created by bot.'''
    try:
        with open(settings.LOG_DIR + 'exec_' + today + '.csv', "r") as handler:
            execs = csv.reader(handler)
            execs = list(execs)
    except:
        print('No executions so far...')
        execs = {}
    return execs

def load_errors():
    '''Load list of errors from csv created by bot.'''
    try:
        with open(settings.LOG_DIR + 'errors_' + today + '.csv', "r") as handler:
            errors = csv.reader(handler)
            errors = list(errors)
    except:
        print('No errors so far...')
        errors = {}
    return errors

def load_orders():
    '''Load list of open orders from csv created by bot.'''
    try:
        with open(settings.LOG_DIR + 'orders_' + today + '.csv', "r") as handler:
            orders = csv.reader(handler)
            orders = [str(o[1] + " " + o[5] + " " + o[6] + " " + o[7] + " " + o[8] + " " + o[9][:14]) for o in list(orders)]
    except:
        orders = {}
    return orders

def load_status():
    '''Load status dictionary from json created by bot.'''
    with open(settings.LOG_DIR + 'current_status.json', "r") as handler:
        status = json.load(handler)
    return status

def load_status_series(length = 1, maxe = False, last = False):
    '''Legacy for reading from status csv logger; used in graph and debug scenarios.'''
    with open(settings.LOG_DIR + 'status_' + today + '.json', "r") as handler:
        unhandled_json = handler.read()

    # Due to the last comma, the actual last entry [-1] is null, so we get the one before that
    if length == 1:
        unhandled_json = str(unhandled_json.split('\n')[-2])
        unhandled_json = unhandled_json[:-1]
        # Wraps [] to json core
        unhandled_json = ''.join(('[',unhandled_json,']'))
    # For time series, we do some serious mangling, but we get there
    elif maxe:
        unhandled_json = str(unhandled_json.split('\n')[0:-2]).replace("'", "").replace(",,", ",").replace("},]", "}]")
    elif last:
        unhandled_json = str(unhandled_json.split('\n')[0])
        unhandled_json = unhandled_json[:-1]
        # Wraps [] to json core
        unhandled_json = ''.join(('[',unhandled_json,']'))
    else:
        cutLength = -(length+2)
        unhandled_json = str(unhandled_json.split('\n')[cutLength:-2]).replace("'", "").replace(",,", ",").replace("},]", "}]")

    # Transforms string to actual json
    handled_json = json.loads(unhandled_json)
    status = handled_json
    return status

def load_initial_balance():
    '''Load initial balance from finantial directory.'''
    with open(settings.FIN_DIR + 'initialBalance.json','rb') as handler:
        my_InitialBalance = json.loads(handler.read())
    return float(my_InitialBalance['initialBalance']) 

def get_profit():
    '''Basic Profit calculation.'''
    initBalance = load_initial_balance()
    lastBalance = load_status()['balance']
    return "{:.2%}".format(((lastBalance - initBalance)/initBalance))

def get_stop_order(orders):
    '''Identifies stop order based on prefix and returns its price.'''
    stop_index = None
    for index, order in enumerate(orders):
        if 'Stm' in order[-1]:
            stop_price = order[2]
            stop_index = index
    if stop_index:
        return stop_price
    else:
        return 0 

# -----------------------------------------------------------------------------------------
# --------------------Dash Callback Functions----------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

@app.callback([Output('status', 'children'),
               Output('timestamp', 'children'),
               Output('open_orders', 'children'),
               Output('profit', 'children'),
               Output('order_num', 'children'),
               Output('position', 'children'),
               Output('stop', 'children'),
               Output('liquidation', 'children'),
               Output('beven', 'children'),
               Output('btc', 'children'),
               Output('volume', 'children'),
               Output('amplitude', 'children'),
               Output('dolmin', 'children'),
               Output('lockAnom', 'children'),
               Output('funds', 'children'),
               Output('margin', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    '''Cyclic upper data update function.'''
    schedule.run_pending() # update today
    statusData = load_status()
    orderList = [(str(order) + '\n') for order in statusData['open_orders']]

    with open(settings.LOG_DIR + 'operation.json', 'r') as r:
        status = json.load(r)
        statusjson = status['operation']
        statusjson = 'Running' if statusjson else 'Paused'

    return [
        str('Instance Status: ' + statusjson),
        str('Last updated: ' + statusData['timestamp']),
        orderList,
        get_profit(),
        statusData['order_num'],
        statusData['position'],
        get_stop_order(statusData['open_orders']),
        statusData['liquidation'],
        statusData['break_even'],
        statusData['latest_price'],
        statusData['volume'] if settings.DEBUG_DASH else statusData['funding_rate'],
        statusData['amplitude'] if settings.DEBUG_DASH else statusData['leverage'],
        statusData['dollar_minute'] if settings.DEBUG_DASH else statusData['avg_entry_price'],
        str(statusData['lock_anomaly']) if settings.DEBUG_DASH else [statusData['ask_price'] - statusData['bid_price']],    
        round(tools.XBt_to_XBT(statusData['balance']),4),
        round(tools.XBt_to_XBT(statusData['available_margin']),4)
    ]

@app.callback([Output('executions', 'children'),
               Output('errors', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_bot_metrics(n):
    '''Cyclic lower data update function.'''
    execData = load_exec()
    errorData = load_errors() if settings.DEBUG_DASH else load_orders()
    execList = [(str(execution) + '\n') for execution in execData]
    errorList = [(str(error) + '\n') for error in errorData]
    return [
        execList.reverse(),
        errorList.reverse()
    ]

@app.callback(Output('count_graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def make_btc_figure(n):
    '''Cyclic XBT price overtime graph update.'''
    statusData = load_status_series(length=0, maxe=True)

    data = [
        dict(
            type='line',
            x=[status['timestamp'] for status in statusData],
            y=[float(status['latest_price']) for status in statusData],
            name='BTC Price',
            marker=dict(
                color= '#FFCD08'
            ),
        ),
    ]

    layout_count = copy.deepcopy(layout)
    layout_count['title'] = None
    layout_count['margin'] = dict(
        l=50,
        r=-10,
        t = 20
    )
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['autosize'] = True
    layout_count['paper_bgcolor'] = 'rgba(0,0,0,0)'
    layout_count['plot_bgcolor'] = 'rgba(0,0,0,0)'
    layout_count['font'] = dict(color='#ebeae3')
    figure = dict(data=data, layout=layout_count)
    return figure

@app.callback(dash.dependencies.Output('pause_message', 'children'),
    [dash.dependencies.Input('pause_button', 'n_clicks'),
    dash.dependencies.Input('pause_confirm', 'cancel_n_clicks_timestamp'),
    dash.dependencies.Input('pause_confirm', 'submit_n_clicks_timestamp')])
def update_output(n_clicks, cancel_n_clicks_timestamp, submit_n_clicks_timestamp):
    '''Bot operation button handling.'''
    username = flask.request.authorization['username']
    if not(cancel_n_clicks_timestamp):
        cancel_n_clicks_timestamp = 1
    if not(submit_n_clicks_timestamp):
        submit_n_clicks_timestamp = 1
    if n_clicks:
        if username in settings.ADMIN_USERS:
            if submit_n_clicks_timestamp > cancel_n_clicks_timestamp:
                with open (settings.LOG_DIR + 'operation.json', 'w') as op:
                    json.dump(dict(operation = True), op)
                settings._PAUSE_BOT = False
                return
            else:
                with open (settings.LOG_DIR + 'operation.json', 'w') as op:
                    json.dump(dict(operation = False), op)
                settings._PAUSE_BOT = True
                return
        else:
            return
    else:
        return

@app.callback([dash.dependencies.Output('html_p1', 'children'),
    dash.dependencies.Output('html_p2', 'children'),
    dash.dependencies.Output('html_p3', 'children'),
    dash.dependencies.Output('html_p4', 'children'),
    dash.dependencies.Output('html_p5', 'children')],
    [Input('interval-component', 'n_intervals')])
def check_user_privilege(n):
    '''Check user admin level and render dashboard accordingly.'''
    username = flask.request.authorization['username']
    if username in settings.ADMIN_USERS:
        settings.DEBUG_DASH = True
        html_p1 = 'Volume'
        html_p2 = 'Amplitude'
        html_p3 = 'Dollar Minute'
        html_p4 = 'Lock Anomaly'
        html_p5 = 'Errors'
    else:
        settings.DEBUG_DASH = False
        html_p1 = 'Funding'
        html_p2 = 'Leverage'
        html_p3 = 'Avg Entry'
        html_p4 = 'Spread'
        html_p5 = 'Order History'
    return [html_p1, html_p2,html_p3,html_p4,html_p5]

@app.callback([dash.dependencies.Output('button_name','children')],
              [Input('interval-component', 'n_intervals')])
def check_button_user(n):
    '''Check user admin level and render run button accordingly.'''
    username = flask.request.authorization['username']
    if username in settings.ADMIN_USERS:
        bn = 'Run Bot'
    else:
        bn = 'In development'
    return [bn]

def run_server():
    print("Dashboard app server started running.")
    app.server.run(host= HOST, port=PORT, debug=settings.DEBUG_DASH, threaded=THREADED_RUN)

# -----------------------------------------------------------------------------------------
# -------------------------- Main ---------------------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

if __name__ == '__main__':
    run_server()