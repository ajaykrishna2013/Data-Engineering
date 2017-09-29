from flask import Flask, session, request, g, redirect, jsonify
from flask import url_for, abort, render_template, flash
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
import json
from datetime import datetime
from flask_cassandra import CassandraCluster
import time

#app = Flask(__name__)
app = Flask('CEP_APP', template_folder="templates")
cassandra = CassandraCluster()

#app.config['CASSANDRA_NODES'] = ['10.0.0.10','10.0.0.12','10.0.0.14']  # can be a string or list of nodes

session = None

@app.route('/')
def render_map():
	global session
	session = cassandra.connect()
	session.set_keyspace("cep_analytics")
	return render_template('leaflet_template.html')

@app.route('/livemapjson')
def fullmap():
    global session
    LAT_LONG = {}
    points = []

    data = get_new_data(session)
    for row in data:
	ll = (row.latitude, row.longitude)
	if ll not in LAT_LONG:
		LAT_LONG[ll] = True
		temp = {}
		temp['lat'] = row.latitude
		temp['lng'] = row.longitude
		temp['event_severity'] = row.event_severity
		temp['event_start_time'] = row.event_start_time
		points.append(temp)
    return jsonify(points)


@app.route('/chart')
def getChart():
	return render_template('leaflet_panel.html')

@app.route('/plot')
def querychart():
    global session
    severity_count = {}
    severity_count['timestamp'] = 0
    severity_count["Medium"] = 0 
    severity_count["Low"] = 0
    severity_count["High"] = 0

    data = get_chart_data(session, int(time.time())*1000 - 5000)
    for row in data:
	if row.event_severity == "Medium":
		severity_count['Medium'] += 1
	elif row.event_severity ==  "Low":
		severity_count['Low'] += 1
	elif row.event_severity ==  "High":
		severity_count['High'] += 1
    severity_count['timestamp'] = int(time.time()) * 1000
    return jsonify(severity_count)

def get_new_data(session):
    cql = "SELECT * FROM cep_analytics.smarthome_cep_table"
    r = session.execute(cql)
    return r

def get_chart_data(session, current_time):
    session.set_keyspace("cep_analytics")  
    cql = "SELECT * FROM cep_analytics.smarthome_cep_table LIMIT 10"
    r = session.execute(cql)
    return r

if __name__ == '__main__':
    with open('config_properties.txt') as f:
	config = f.readlines()
    app.config['CASSANDRA_NODES'] = [config[0],config[1],config[2]]  # can be a string or list of nodes
    app.run(host='ec2-50-112-18-158.us-west-2.compute.amazonaws.com')
