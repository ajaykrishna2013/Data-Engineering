from SmartHome import SmartHome
from confluent_kafka import Producer
import csv
import os
from datetime import datetime, timedelta
import json
import time
import sys
import random

class SmartHomeProducer():
	def __init__(self, kafka_cfg):
        	self.step = timedelta(seconds=1)
        	self.duration = timedelta(days=1)
		self.startTime = datetime.now()
		self.endTime = self.startTime + self.duration
		self.proc = Producer(kafka_cfg)

	def transmit_home_data(self, infile):
                with open(infile, 'rb') as f:
                        reader = csv.DictReader(f)
                        count = 0
			total_count = 0
                        allMeter = []
                        for row in reader:
                                allMeter.append(row)
                        for row in allMeter:
                                count += 1
                                eventTime = self.startTime + self.step
                                eventTimestamp = str(eventTime)
                                row['time'] = eventTimestamp
                                self.proc.produce('SHMeterTopic2', json.dumps(row))
                                self.startTime = eventTime
                                if count == 1000:
					total_count += count
					if total_count == 40000: break
                                        delay = random.uniform(0,2)
                                        time.sleep(delay)
					count = 0
                return total_count    

if __name__ == '__main__':
	infile = sys.argv[1]
	config = sys.argv[2]
	kafka_config = {}
	with open(config, 'r') as cfg:
		config = cfg.readlines()
		server, address = config[0].rstrip('\n').split('=')
	kafka_config[server] = address
	home1 = SmartHomeProducer(kafka_config)
	startTime = time.time()
	count = home1.transmit_home_data(infile)
	time_taken = time.time() - startTime
	print 'sent %d events in %f' % (count, time_taken) 
	
