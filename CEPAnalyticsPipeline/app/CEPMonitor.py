from flask import Flask, session, request, g, redirect, jsonify
from flask import url_for, abort, render_template, flash, redirect
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
import json
from datetime import datetime
from flask_cassandra import CassandraCluster
import time

#app = Flask(__name__)
app = Flask('CEP_APP', template_folder="templates")
cassandra = CassandraCluster()


with open('config_properties.json') as data_file:    
    config = json.load(data_file)
 
app.config['CASSANDRA_NODES'] = [config['Node1'], config['Node2'], config['Node3']]

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

@app.route('/demo_slides')
def demo_slides():
	return redirect(config['demo_slides'])

@app.route('/github')
def github():
	return redirect(config['github'])



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
    app.run(host='0.0.0.0')
