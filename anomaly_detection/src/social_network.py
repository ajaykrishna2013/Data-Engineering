from collections import defaultdict, OrderedDict
from users import User
from search_within_degree import Search
import numpy as np
import json
import heapq
import logging

class SocialNetwork():
	def __init__(self, logfile, d=1, T=2):
		"""
		Creates a new SocialNetwork with parameters D and T
		Args:
		    logfile:
		    d:
		    T:
		"""
		#self.logger = logging.getLogger(__name__)
		#self.logger.setLevel(logging.DEBUG)
		# fh = logging.FileHandler('social_network.log')
		# fh.setLevel(logging.DEBUG)
		# self.logger.addHandler(fh)
		self.network = defaultdict(list)
		self.degree = d
		self.num_tracked = T
		self.output_log = logfile
		#self.logger.info('Created SocialNetwork')

	def get_size(self):
		return len(self.network.keys())

	def get_users(self):
		return self.network.keys()

	def get_friend_ids(self, user_id):
		return self.network[user_id].get_friends()

	def get_degree(self, user_id):
		return len(self.network[user_id].get_degree())

	def add_user(self, user):
		"""
		Adds user to the network
		Args:
		    user:

		Returns:

		"""
		#self.logger.info('Adding user %s', user.get_userid())
		user_id = user.get_userid()
		self.network[user_id] = user

	def add_friend(self, user1_id, user2_id):
		"""
		Checks if either of the users indexed by user id is in the network
		if one of them is not in the nework, creates and adds that user and
		then connects the 2 users

		If both users don't exist in the network, creates both, adds them to the
		network and connects them
		Args:
		    user1_id:
		    user2_id:

		Returns:

		"""
		if (user1_id in self.network or user2_id in self.network):
			if user1_id in self.network and not user2_id in self.network:
				#self.logger.info("User %s does not exist in network.", user2_id)
				# create user 2
				user2 = User(user2_id, self.num_tracked)
				self.add_user(user2)
			elif not user1_id in self.network and user2_id in self.network:
				#self.logger.info("User %s does not exist in network.", user1_id)
				# create user 1
				user1 = User(user1_id, self.num_tracked)
				self.add_user(user1)
		else:
			#self.logger.info("User %s and %s do not exist in network.", user1_id, user2_id)
			user1 = User(user1_id, self.num_tracked)
			user2 = User(user2_id, self.num_tracked)
			self.add_user(user1)
			self.add_user(user2)

		self.network[user1_id].add_friend(user2_id)
		self.network[user2_id].add_friend(user1_id)


	def remove_friend(self, user1_id, user2_id):
		"""
		Calls the remove api of a users indexed by ids.
		Removes user2 from user1's friends list and
		removes user1 from user2's friends list
		Args:
		    user1_id:
		    user2_id:

		Returns:
		    nothing

		"""
		if (user1_id in self.network or user2_id in self.network):
			self.network[user1_id].remove_friend(user2_id)
			self.network[user2_id].remove_friend(user1_id)
		else:
			#self.logger.info("Users %s and %s not in network, Cannot remove", user1_id, user2_id)
			pass

	def check_anamoly_and_update_network(self, user_id, purchase):
		"""
		Gets friends with in the degree, checks anomaly and write to flagged_purchases.json
		if purchase is anomaly.
		Adds current purchase to user's purchases
		Args:
		    user_id:
		    purchase:

		Returns:
		    is_anomaly, mean, std

		"""
		if user_id in self.network:
			friend_list = self.get_friends_within_degree(user_id)
			#self.logger.info('Friend list for user %s: %s', user_id, friend_list)

			T = self.network[user_id].get_num_tracked()
			is_anomaly, mean, std = self.check_anomaly(friend_list, purchase, T)

			#self.logger.info("current purchase: %s", purchase)
			#self.logger.info('is_anomaly = %r mean = %f std = %f', is_anomaly, mean, std)


			# Build the flagged purchase json object and write to flagged_purchases.json
			flagged_purchase = OrderedDict()
			if is_anomaly:
				flagged_purchase['event_type'] = 'purchase'
				flagged_purchase['timestamp'] = purchase[1]
				flagged_purchase['id'] = user_id
				flagged_purchase['amount'] = "{0:.2f}".format(purchase[2])
				flagged_purchase['mean'] = "{0:.2f}".format(mean)
				flagged_purchase['sd'] = "{0:.2f}".format(std)

				json_string = json.dumps(flagged_purchase)
				#with open('.' + self.output_log, 'a') as f:
				with open(self.output_log, 'a+') as f:
					f.write(json_string)
					f.write('\n')

			#self.logger.info("Add current purchase %s for user %s", purchase, user_id)

			# Add the current purchase to the user's purchase list
			user = self.network[user_id]
			user.add_purchase(purchase)
			return is_anomaly, mean, std
		else:
			#self.logger.info("user: %s not in network.", user_id)
			user = User(user_id, self.num_tracked)
			# add his purchase
			user.add_purchase(purchase)
			# add user to network
			self.add_user(user)
			return None, None, None

	def get_friends_within_degree(self, user_id):
		"""
		Creates a search object and uses the get_friends_within_degree
		to get all friends within the degree
		Args:
		    user_id:

		Returns:
		    friends list

		"""
		search_obj = Search(self.network, self.degree, user_id)
		return search_obj.get_friends_within_degree()

	def check_anomaly(self, friend_list, purchase, T):
		"""
		Gets the purchases from the friends list and
		merges them into one list and picks the largest T purchases
		based on sequence numbers. These are the latests purchases

		Calculates mean and standard deviation and checks if
		current purchase is an anomaly.
		Args:
		    friend_list:
		    purchase:
		    T:

		Returns: True/False for anomaly, mean and standard deviation

		"""
		all_purchases = []

		for friend_id in friend_list:
			friend = self.network[friend_id]
			purchases_of_friend = friend.get_purchases()
			all_purchases.extend(purchases_of_friend)

		# K way merge
		#temp = heapq.merge(*all_purchases)
		#temp_list = [t for t in temp]

		# heapify all purchases instead
		heapq.heapify(all_purchases)
		top_T_purchases = []
		for i in range(int(self.num_tracked)):
			if all_purchases:
				top_T_purchases.append(heapq.heappop(all_purchases))

		#self.logger.info('All purchases in network of degree D: %s', temp_list)
		#top_T_purchases = heapq.nlargest(int(self.num_tracked), all_purchases, key=lambda x: -1 * x[0])
		#self.logger.info('Most recent T purchases in network: %s', top_T_purchases)

		if len(top_T_purchases) == 0:
			mean_of_purchases = 0
			standard_deviation = 0
		else:
			mean_of_purchases = np.mean([p[2] for p in top_T_purchases])
			standard_deviation = np.std([p[2] for p in top_T_purchases])

		if purchase[2] > (mean_of_purchases + (3 * standard_deviation)):
			return True, mean_of_purchases, standard_deviation
		return False, mean_of_purchases, standard_deviation

	def _get_purchases(self, user_id):
		"""
		Debug function. Not used for regular use case
		Args:
		    user_id:

		Returns:
		    tuple of len, list and top T purchases

		"""
		friend_list = self.get_friends_within_degree(user_id)
		all_purchases = []
		for friend_id in friend_list:
			friend = self.network[friend_id]
			purchases_of_friend = friend.get_purchases()
			all_purchases.append(purchases_of_friend)


		temp = heapq.merge(*all_purchases)
		temp_list = [t for t in temp]
		top_T_purchases = heapq.nlargest(int(self.num_tracked), temp_list, key=lambda x: x[2])

		return len(temp_list), temp_list, top_T_purchases

	def _get_purchases_from_friend_list(self, friend_list):
		"""
		Debug function. Not used for regular use case
		Args:
			user_id:

		Returns:
			tuple of len, list and top T purchases

		"""
		purchases_of_friend = {}
		for friend_id in friend_list:
			friend = self.network[friend_id]
			purchases_of_friend[friend_id] = friend.get_purchases()

		return purchases_of_friend


if __name__ == '__main__':
	pass
	# import random
	# import time
	# import pprint

	#random.seed(101)
	# purchases = []
	# with open('data/tinyGPurchases.json', 'a+') as f:
	# 	for transactions in range(0, 50):
	# 		transaction = {}
	# 		amount = round(random.uniform(1.0, 500.0), 2)
	# 		user = random.randint(0,12)
	# 		timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
	#
	# 		# fill transaction
	# 		transaction['event_type'] = "purchase"
	# 		transaction['id'] = str(user)
	# 		transaction['amount'] = str(amount)
	# 		transaction['timestamp'] = str(timestamp)
	# 		purchases.append(transaction)
	# 		t = random.uniform(0.2,0.8)
	# 		time.sleep(t)
	#
	# 	purchases.sort(key=lambda x: x['timestamp'])
	# 	for purchase in purchases:
	# 		json_str = json.dumps(purchase)
	# 		f.write(json_str)
	# 		f.write('\n')

	# with open('data/tinyG.txt', 'r') as f:
	# 	V = int(f.readline().rstrip('\n'))
	# 	E = int(f.readline().rstrip('\n'))
	#
	# 	with open('data/friendships.json', 'a') as f2:
	# 		for j in range(0, E):
	# 			friendship = {}
	# 			l = f.readline().rstrip('\n').split(' ')
	#
	# 			friendship["event_type"] = "befriend"
	# 			friendship["timestamp"] = str(random.randint(0, 10))
	# 			friendship["id1"] = str(l[0])
	# 			friendship["id2"] = str(l[1])
	# 			json_str = json.dumps(friendship)
	# 			f2.write(json_str)
	# 			f2.write('\n')

	# batch_input_file = './small_sample_dataset/batch_log.json'
	# stream_input_file = './small_sample_dataset/stream_log.json'
	# flagged_purchases_output = './small_sample_dataset/flagged_purchases'
	# fptr = open('debug.log', 'a')
	#
	# for degree in range(1, 4):
	# 	for tracked_size in range(2, 10):
	# 		banner_id = str(degree) + '_' + str(tracked_size)
	# 		index = 0
	# 		social_network = SocialNetwork(flagged_purchases_output + banner_id + '.json', degree, tracked_size)
	# 		with open('.' + batch_input_file, 'r') as f:
	# 			for idx, line in enumerate(f.readlines()):
	# 				line.rstrip()
	# 				json_line = json.loads(line)
	# 				if json_line['event_type'] == 'purchase':
	#
	# 					timestamp = json_line['timestamp']
	# 					purchase_amount = float(json_line['amount'])
	# 					purchase = (purchase_amount, timestamp, index)
	# 					user_id = json_line['id']
	#
	# 					if not user_id in social_network.network:
	# 						# create user
	# 						user = User(user_id, tracked_size)
	# 						# add his purchase
	# 						user.add_purchase(purchase)
	# 						# add user to network
	# 						social_network.add_user(user)
	# 					else:
	# 						user = social_network.network[user_id]
	# 						user.add_purchase(purchase)
	# 				elif json_line['event_type'] in ['befriend', 'unfriend']:
	# 					user1_id = json_line['id1']
	# 					user2_id = json_line['id2']
	# 					timestamp = json_line['timestamp']
	# 					event_type = json_line['event_type']
	#
	# 					if event_type == 'befriend':
	# 						social_network.add_friend(user1_id, user2_id)
	# 					elif event_type == 'unfriend':
	# 						social_network.remove_friend(user1_id, user2_id)
	# 				index += 1
	#
	# 		# with open('debug'+file_id+'.log', 'a') as fptr:
	# 		# 	for k in range(0, 3):
	# 		# 		print >>fptr, 'User = %d Degree = %d track size = %d' % (k, degree, tracked_size)
	# 		# 		print >>fptr, 'Friends', social_network.get_friends_within_degree(str(k))
	# 		# 		print >>fptr, 'total purchases of network: %d\n\nall purchases: %s\n\ntop T purchases from network:%s\n' % social_network._get_purchases(str(k))
	#
	#
	# 		with open('.' + stream_input_file) as s:
	# 			print >> fptr, '####################################'
	# 			print >> fptr, 'DEGREE_TRACK SIZE: %s' % (banner_id)
	# 			print >> fptr, '####################################'
	# 			for idx, line in enumerate(s.readlines()):
	# 				line.rstrip()
	# 				try:
	# 					json_line = json.loads(line)
	#
	# 					if json_line['event_type'] == 'purchase':
	# 						timestamp = json_line['timestamp']
	# 						purchase_amount = float(json_line['amount'])
	# 						purchase = (purchase_amount, timestamp, index)
	# 						user_id = json_line['id']
	# 						is_anomaly, mean, std = social_network.check_anamoly_and_update_network(user_id, purchase)
	#
	# 						# get debug information
	# 						#with open('debug'+banner_id+ '.log', 'a') as fptr:
	# 						friends = social_network.get_friends_within_degree(user_id)
	# 						all_purchases = social_network._get_purchases_from_friend_list(friends)
	# 						total_purchases = 0
	# 						for v in all_purchases.values():
	# 							total_purchases += len(v)
	#
	# 						print >>fptr, 'Current User %s Current Amount %f num_friends %d purchases in network %d Degree = %d track size = %d' % (user_id, purchase_amount, len(friends), total_purchases, degree, tracked_size)
	# 						for user, p in all_purchases.items():
	# 							print >>fptr, 'friend_id %s purchase = %s' %(user, p)
	# 						print >>fptr, 'top T purchases from network:%s' % social_network._get_purchases(str(user_id))[2]
	# 						if is_anomaly != None:
	# 							print >>fptr, 'anomaly_threshold %f Current Amount %f is_anomaly %r' % (mean + (3 * std), purchase_amount, is_anomaly)
	# 						print >>fptr, '\n'
	#
	# 					elif json_line['event_type'] in ['befriend', 'unfriend']:
	# 						user1_id = json_line['id1']
	# 						user2_id = json_line['id2']
	# 						timestamp = json_line['timestamp']
	# 						event_type = json_line['event_type']
	#
	# 						if event_type == 'befriend':
	# 							social_network.add_friend(user1_id, user2_id)
	# 						elif event_type == 'unfriend':
	# 							social_network.remove_friend(user1_id, user2_id)
	# 				except ValueError:
	# 					print 'Error'
	# 				index += 1

			#print 'Next track size'
		#print 'next degree for network'



