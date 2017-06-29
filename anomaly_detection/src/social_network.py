from collections import defaultdict, OrderedDict
from users import User
from search_within_degree import Search
import numpy as np
import json

class SocialNetwork():
	def __init__(self, logfile, d=1):
		self.network = defaultdict(list)
		self.degree = d
		self.output_log = logfile

	def add_user(self, user):
		user_id = user.get_userid()
		self.network[user_id] = user

	def add_friend(self, user1_id, user2_id):
		if (user1_id in self.network or user2_id in self.network):

			if user1_id in self.network and not user2_id in self.network:
				# create user 2
				user2 = User(user2_id)
				self.add_user(user2)
			elif not user1_id in self.network and user2_id in self.network:
				# create user 1
				user1 = User(user1_id)
				self.add_user(user1)

			self.network[user1_id].add_friend(user2_id)
			self.network[user2_id].add_friend(user1_id)


	def remove_friend(self, user1_id, user2_id):
		if (user1_id in self.network or user2_id in self.network):
			self.network[user1_id].remove_friend(user2_id)
			self.network[user2_id].remove_friend(user1_id)

	def get_friend_ids(self, user_id):
		return self.network[user_id].get_friends()

	def get_degree(self, user_id):
		return len(self.network[user_id].get_degree())

	def check_anamoly_and_update_network(self, user_id, purchase):
		is_anomaly, mean, std = self.get_friends_within_degree(user_id, purchase)

		flagged_purchase = OrderedDict()
		if is_anomaly:
			flagged_purchase['event_type'] = 'purchase'
			flagged_purchase['timestamp'] = purchase[1]
			flagged_purchase['id'] = user_id
			flagged_purchase['amount'] = str(purchase[0])
			flagged_purchase['mean'] = str(round(mean, 2))
			flagged_purchase['sd'] = str(round(std, 2))

			json_string = json.dumps(flagged_purchase)
			with open('.' + self.output_log, 'a+') as f:
				f.write(json_string)


		user = self.network[user_id]
		user.add_purchase(purchase)
		total_number_of_purchases = 0
		# go through friends list
		# find mean and standard deviation
		# check for anaomaly
		# set return value to True or update file from here
		# add purchase to user's purchase list

	def get_friends_within_degree(self, user_id, purchase):
		search_obj = Search(self.network, self.degree, user_id)

		purchases = []

		for friend_id in search_obj.get_friends_within_degree():
			friend = self.network[friend_id]
			purchases_of_friend = friend.get_purchases()
			purchases.extend(purchases_of_friend)

		#user = self.network[user_id]
		#purchases.extend(user.get_purchases())

		mean_of_purchases = np.mean([p[0] for p in purchases])
		standard_deviation = np.std([p[0] for p in purchases])

		if purchase[0] > (mean_of_purchases + (3 * standard_deviation)):
			return True, mean_of_purchases, standard_deviation
		return False


