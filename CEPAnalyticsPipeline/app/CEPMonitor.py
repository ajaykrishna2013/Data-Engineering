from flask import Flask, session, request, g, redirect
from flask import url_for, abort, render_template, flash
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons


from flask_cassandra import CassandraCluster

#app = Flask(__name__)
app = Flask('CEP_APP', template_folder="templates")
cassandra = CassandraCluster()

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBoPGosMrPNnkh5uULucFBKaq52b2i71uc"

# you can also pass key here
GoogleMaps(app, key="AIzaSyBoPGosMrPNnkh5uULucFBKaq52b2i71uc")

app.config['CASSANDRA_NODES'] = ['10.0.0.10','10.0.0.12','10.0.0.14']  # can be a string or list of nodes


@app.route('/livemap')
def fullmap():
    session = cassandra.connect()
    session.set_keyspace("cep_analytics")
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
		points.append(temp)
    return go_render_map(points)

def go_render_map(points):
    	fullmap = Map(
    	    identifier="fullmap",
    	    varname="fullmap",
    	    style=(
    	        "height:100%;"
    	        "width:100%;"
    	        "top:0;"
    	        "left:0;"
    	        "position:absolute;"
    	        "z-index:100;"
    	    ),
    	    lat=37.4419,
    	    lng=-122.1419,
	    markers = points,
    	)
    	return render_template('example_fullmap.html', fullmap=fullmap)

def get_new_data(session):
    cql = "SELECT * FROM cep_analytics.smarthome_cep_table LIMIT 50"
    r = session.execute(cql)
    return r

@app.route("/cassandra_test")
def cassandra_test():
    session = cassandra.connect()
    session.set_keyspace("cep_analytics")
    cql = "SELECT * FROM cep_analytics.smarthome_cep_table LIMIT 50"
    r = session.execute(cql)
    return render_template('event_table.html', data=r)

if __name__ == '__main__':
    app.run(host='ec2-50-112-18-158.us-west-2.compute.amazonaws.com')
