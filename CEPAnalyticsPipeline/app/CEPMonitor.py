from flask import Flask, session, request, g, redirect
from flask import url_for, abort, render_template, flash
from flask_cassandra import CassandraCluster

app = Flask(__name__)
cassandra = CassandraCluster()

app.config['CASSANDRA_NODES'] = ['10.0.0.10','10.0.0.12','10.0.0.14']  # can be a string or list of nodes

@app.route("/cassandra_test")
def cassandra_test():
    session = cassandra.connect()
    session.set_keyspace("test")
    cql = "SELECT * FROM smart_home.smarthome_event_usage LIMIT 50"
    r = session.execute(cql)
    return render_template('event_table.html', data=r)
#    print 'R', r
#    for e in r:
#	print e, type(e)
#	try:
#		print e.element1,
#		print e.element2
#	except:
#		print "Something funky going on"

if __name__ == '__main__':
    app.run(host='ec2-50-112-18-158.us-west-2.compute.amazonaws.com')
