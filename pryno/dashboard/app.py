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
# from flask_login import user_logged_in
from flask import Flask, request
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
# import dash_auth
from pryno.util import settings, tools
from pryno.dashboard import client_dash
import time
from threading import Timer
# This makes the app silent on console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Needed for single main.py file
THREADED_RUN = True

# Make 80 for AWS EC2, default is 5000
PORT = 80

#Is resetting
is_resetting = False

# Make 0.0.0.0 to IP redirect, default is 127.0.0.1
HOST = '0.0.0.0'

# Creating webapp
app = dash.Dash(__name__)

server = app.server

# Datetime update
today = dt.datetime.today().strftime('%Y-%m-%d')


def update_today():
    today = dt.datetime.today().strftime('%Y-%m-%d')
    return today


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


def load_status_series(length=1, maxe=False, last=False):
    '''Legacy for reading from status csv logger; used in graph and debug scenarios.'''
    with open(settings.LOG_DIR + 'status_' + today + '.json', "r") as handler:
        unhandled_json = handler.read()

    # Due to the last comma, the actual last entry [-1] is null, so we get the one before that
    if length == 1:
        unhandled_json = str(unhandled_json.split('\n')[-2])
        unhandled_json = unhandled_json[:-1]
        # Wraps [] to json core
        unhandled_json = ''.join(('[', unhandled_json, ']'))
    # For time series, we do some serious mangling, but we get there
    elif maxe:
        unhandled_json = str(unhandled_json.split('\n')[0:-2]).replace("'", "").replace(",,", ",").replace("},]", "}]")
    elif last:
        unhandled_json = str(unhandled_json.split('\n')[0])
        unhandled_json = unhandled_json[:-1]
        # Wraps [] to json core
        unhandled_json = ''.join(('[', unhandled_json, ']'))
    else:
        cutLength = -(length+2)
        unhandled_json = str(unhandled_json.split('\n')[cutLength:-2]).replace("'", "").replace(",,", ",").replace("},]", "}]")

    # Transforms string to actual json
    handled_json = json.loads(unhandled_json)
    status = handled_json
    return status


def load_initial_balance():
    '''Load initial balance from finantial directory.'''
    with open(settings.FIN_DIR + 'initialBalance.json', 'rb') as handler:
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
    schedule.run_pending()  # update today
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
        round(tools.XBt_to_XBT(statusData['balance']), 4),
        round(tools.XBt_to_XBT(statusData['available_margin']), 4)
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
                color='#FFCD08'
            ),
        ),
    ]

    layout_count = copy.deepcopy(layout)
    layout_count['title'] = None
    layout_count['margin'] = dict(
        l=50,
        r=-10,
        t=20
    )
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['autosize'] = True
    layout_count['paper_bgcolor'] = 'rgba(0,0,0,0)'
    layout_count['plot_bgcolor'] = 'rgba(0,0,0,0)'
    layout_count['font'] = dict(color='#ebeae3')
    figure = dict(data=data, layout=layout_count)
    return figure




@app.callback([dash.dependencies.Output('html_p1', 'children'),
    dash.dependencies.Output('html_p2', 'children'),
    dash.dependencies.Output('html_p3', 'children'),
    dash.dependencies.Output('html_p4', 'children'),
    dash.dependencies.Output('html_p5', 'children')],
    [Input('interval-component', 'n_intervals')])
def Set_Debug_Mode(n):
    '''Check user admin level and render dashboard accordingly.'''
    settings.DEBUG_DASH = True #change this accordingly with the information you desire to see on Dashboard
    # if Debug is false you see another set of information at user screen
    if settings.DEBUG_DASH:
        html_p1 = 'Volume'
        html_p2 = 'Amplitude'
        html_p3 = 'Dollar Minute'
        html_p4 = 'Lock Anomaly'
        html_p5 = 'Errors'
    else:

        html_p1 = 'Funding'
        html_p2 = 'Leverage'
        html_p3 = 'Avg Entry'
        html_p4 = 'Spread'
        html_p5 = 'Order History'
    return [html_p1, html_p2, html_p3, html_p4, html_p5]




# -----------------------------------------------------------------------------------------
# ----------------------- Server Functions ------------------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------


def run_server():
    print(f"""
    
    Dashboard app server started running!

    _____________________________________________________ 
                                                      
            Access URL:                                
            -------------------------------            
            Localhost: http://127.0.0.1:{PORT}             
                                                      
    _____________________________________________________

    
    """)
    pid = os.getpid()
    response = os.popen("ps -ef | grep python")
    print(response)
    with open('pids/app.pid', 'w') as w:
        w.write(str(pid))
    app.server.run(host=HOST, port=PORT, debug=settings.DEBUG_DASH, threaded=THREADED_RUN)


def shutdown_server():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@server.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'



#endpoint to reset bot process, if some server update or thing like that is sent
@server.route('/reset', methods=['POST'])
def process_json():
    input_json = flask.request.get_json()
    # the pwd parameter is hardcoded for now
    if input_json.get('pwd') == 'bot_Reset':
        r2 = Timer(4.0, shutdown_server)
        r1.start()
        r2.start()
        return 'Reseting bot', 200
    else:
        return 'Wrong credentials', 400



# the below routes are for checkin applications log on the webpage
@server.route('/api')
def api_data():
    if(flask.request.authorization):
        filename = 'api_' + dt.datetime.today().strftime('%Y-%m-%d') + '.txt'
        complete_path = settings.LOG_DIR + filename
        with open (complete_path, 'r') as r:
            data = r.read()
            data = data.split('\n')
            data.reverse()
            return flask.render_template('logs.html', filename = filename, data = data,
                                         account = settings.CLIENT_NAME, lastup = str(dt.datetime.now()))
    else:
        return flask.render_template('unauthorized.html')


@server.route('/errors')
def error_data():
    if(flask.request.authorization):
        filename = 'errors_' + dt.datetime.today().strftime('%Y-%m-%d') + '.txt'
        complete_path = settings.LOG_DIR + filename
        with open (complete_path, 'r') as r:
            data = r.read()
            data = str(data).split('\n')
            data.reverse()
            return flask.render_template('logs.html', filename = filename, data = data,
                                     account = settings.CLIENT_NAME, lastup = str(dt.datetime.now()))
    else:
        return flask.render_template('unauthorized.html')

@server.route('/subsonicevilneedle')
def pps_data():
    if(flask.request.authorization):
        filename = 'pps_' + dt.datetime.today().strftime('%Y-%m-%d') + '.txt'
        complete_path = settings.LOG_DIR + filename
        with open (complete_path, 'r') as r:
            data = r.read()
            data = data.split('\n')
            data.reverse()
            return flask.render_template('logs.html', filename = filename, data = data,
                                         account = settings.CLIENT_NAME, lastup = str(dt.datetime.now()))
    else:
        return flask.render_template('unauthorized.html')


@server.route('/status')
def status_data():
    if(flask.request.authorization):
        filename = 'status_' + dt.datetime.today().strftime('%Y-%m-%d') + '.json'
        complete_path = settings.LOG_DIR + filename
        data = load_status_series(length=0, maxe=True)
        data.reverse()
        return flask.render_template('logs.html', filename = filename, data = data,
                                    account = settings.CLIENT_NAME, lastup = str(dt.datetime.now()))
    else:
        return flask.render_template('unauthorized.html')

if __name__ == '__main__':
    run_server()
