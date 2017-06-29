import json
import sys
import os.path
from social_network import SocialNetwork
from users import User


def process_batch_input(social_network, batch_input_file):
	with open('.' + batch_input_file, 'r') as f:
		for idx, line in enumerate(f.readlines()):
			line.rstrip()
			json_line = json.loads(line)
			if 'D' in json_line:
				degree = json_line['D']
				num_tracked = json_line['T']
				social_network = SocialNetwork(degree)
			elif json_line['event_type'] == 'purchase':
				timestamp = json_line['timestamp']
				purchase_amount = json_line['amount']
				purchase = (purchase_amount, timestamp)
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

				if (user1_id in social_network.network or user2_id in social_network.network):

					if event_type == 'befriend':
						if user1_id in social_network.network and not user2_id in social_network.network:
							# create user
							user2 = User(user2_id)
							social_network.add_user(user2)
							social_network.add_friend(user1_id, user2_id)
						elif not user1_id in social_network.network and user2_id in social_network.network:
							# create user
							user1 = User(user1_id)
							social_network.add_user(user1)
							social_network.add_friend(user1_id, user2_id)
						else:
							social_network.add_friend(user1_id, user2_id)
					elif event_type == 'unfriend':
						social_network.remove_friend(user1_id, user2_id)


if __name__ =='__main__':
	batch_input, event_input, output_log = sys.argv[1:]
	print 'batch input', batch_input
	print 'envent input', event_input
	print 'output_log', output_log

	num_tracked = 0
	degree = 0

	social_network = None
	process_batch_input(social_network, batch_input)


