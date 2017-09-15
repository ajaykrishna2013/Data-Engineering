from SmartHome import SmartHome
from confluent_kafka import Producer
import csv
import os
from datetime import datetime, timedelta
import json

class SmartHomeProducer():
	def __init__(self):
        	self.step = timedelta(seconds=1)
        	self.duration = timedelta(days=1)
		self.startTime = datetime.now()
		self.endTime = self.startTime + self.duration
		self.proc = Producer({'bootstrap.servers':'54.69.161.38:9092'})
		
	def transmit_home_data(self):
		with open('HomeA-meter2_2016.csv', 'rb') as f:
			reader = csv.DictReader(f)
			for row in reader:
				eventTime = self.startTime + self.step
				eventTimestamp = eventTime.strftime("%s")
				row['Date & Time'] = eventTimestamp
				row['LAT'] = 37.216953
				row['LONG'] = -121.926555
				self.proc.produce('first_topic', json.dumps(row))
				print raw_input('?')
				self.startTime = eventTime
	


if __name__ == '__main__':
	home1 = SmartHomeProducer()
	home1.transmit_home_data()
