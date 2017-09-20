from SmartHome import SmartHome
from confluent_kafka import Producer
import csv
import os
from datetime import datetime, timedelta
import json
import time

class SmartHomeProducer():
	def __init__(self):
        	self.step = timedelta(seconds=1)
        	self.duration = timedelta(days=1)
		self.startTime = datetime.now()
		self.endTime = self.startTime + self.duration
		self.proc = Producer({'bootstrap.servers':'54.69.161.38:9092'})
		
	def transmit_home_data(self):
		with open('HomeAMeter.csv', 'rb') as f:
			reader = csv.DictReader(f)
			count = 0
			for row in reader:
				#print self.startTime
				eventTime = self.startTime + self.step
				eventTimestamp = str(eventTime)
				row['time'] = eventTimestamp
				#print row['time'], row['usage']
				self.proc.produce('SmartHomeMeterTopic', json.dumps(row))
				self.startTime = eventTime
				count += 1
				if count == 50000:
					break		
		return count


if __name__ == '__main__':
	home1 = SmartHomeProducer()
	startTime = time.time()
	count = home1.transmit_home_data()
	time_taken = time.time() - startTime
	print 'sent %d events in %f' % (count, time_taken) 
	
