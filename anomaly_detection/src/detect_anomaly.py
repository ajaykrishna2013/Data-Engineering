import json
import sys
import os.path
from social_network import SocialNetwork
from users import User
import logging
import time
import cProfile

index = 0


def process_batch_input(batch_input_file, output_log, logger):
	global index

	#with open('.' + batch_input_file, 'r') as f:
	with open(batch_input_file, 'r') as f:
		for idx, line in enumerate(f.readlines()):
			#logger.info('File %s: Processing line numer: %d', batch_input_file, idx)
			line.rstrip()
			json_line = json.loads(line)
			if 'D' in json_line:
				degree = json_line['D']
				num_tracked = json_line['T']
				#logger.info('Degree of network = %s number of tracked purchases = %s', degree, num_tracked)
				social_network = SocialNetwork(output_log, degree, num_tracked)
			elif json_line['event_type'] == 'purchase':
				timestamp = json_line['timestamp']
				purchase_amount = float(json_line['amount'])
				purchase = (-1*index, timestamp, purchase_amount)
				user_id = json_line['id']

				if not user_id in social_network.network:
					# create user
					user = User(user_id, num_tracked)
					# add his purchase
					user.add_purchase(purchase)
					# add user to network
					social_network.add_user(user)
				else:
					user = social_network.network[user_id]
					user.add_purchase(purchase)
			elif json_line['event_type'] in ['befriend', 'unfriend']:
				user1_id = json_line['id1']
				user2_id = json_line['id2']
				timestamp = json_line['timestamp']
				event_type = json_line['event_type']

				if event_type == 'befriend':
					social_network.add_friend(user1_id, user2_id)
				elif event_type == 'unfriend':
					social_network.remove_friend(user1_id, user2_id)
			index += 1
	return social_network


def process_event_input(social_network, event_input_file,logger):
	global index

	#with open('.' + event_input_file, 'r') as f:
	with open(event_input_file, 'r') as f:
		for idx, line in enumerate(f.readlines()):
			#logger.info('File %s: Processing line numer: %d', event_input_file, idx)
			line.rstrip()
			try:
				json_line = json.loads(line)

				if json_line['event_type'] == 'purchase':
					timestamp = json_line['timestamp']
					purchase_amount = float(json_line['amount'])
					purchase = (-1*index, timestamp, purchase_amount)
					user_id = json_line['id']
					social_network.check_anamoly_and_update_network(user_id, purchase)
				elif json_line['event_type'] in ['befriend', 'unfriend']:
					user1_id = json_line['id1']
					user2_id = json_line['id2']
					timestamp = json_line['timestamp']
					event_type = json_line['event_type']

					if event_type == 'befriend':
						social_network.add_friend(user1_id, user2_id)
					elif event_type == 'unfriend':
						social_network.remove_friend(user1_id, user2_id)
			except ValueError:
				logger.info('File %s: Processing line: %s', event_input_file, line)
			index += 1


def main():
	batch_input, event_input, output_log = sys.argv[1:]
	#print 'batch input', batch_input
	#print 'event input', event_input
	#print 'output_log', output_log

	logger = logging.getLogger(__name__)
	num_tracked = 0
	degree = 0

	#profile = cProfile.Profile()


	try:
		#start = time.time()
		#print 'processing batch'

		social_network = process_batch_input(batch_input, output_log, logger)

		#print 'Time to process batch log', time.time() - start
		#print 'processing stream'
		#start2 = time.time()
		#profile.enable()

		process_event_input(social_network, event_input, logger)

		#print 'Time to process stream log', time.time() - start2
		#profile.disable()
	finally:
		pass
		#profile.print_stats()

if __name__ =='__main__':
	logging.basicConfig(level=logging.DEBUG,
						filename='anomaly_detection.log',
						format='%(name)s: %(message)s')
	main()



