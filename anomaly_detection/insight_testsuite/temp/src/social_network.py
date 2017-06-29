from collections import defaultdict
from users import User

class SocialNetwork():
	def __init__(self, d=1):
		self.network = defaultdict(list)
		self.degree = d

	def add_user(self, user):
		user_id = user.get_userid()
		self.network[user_id] = user

	def add_friend(self, user1_id, user2_id):
		self.network[user1_id].add_friend(user2_id)
		self.network[user2_id].add_friend(user1_id)

	def remove_friend(self, user1_id, user2_id):
		self.network[user1_id].remove_friend(user2_id)
		self.network[user2_id].remove_friend(user1_id)

	def get_friend_ids(self, user_id):
		return self.network[user_id].get_friends()

	def get_degree(self, user_id):
		return len(self.network[user_id].get_degree())

	def get_friends_upto_degree(self, degree):
		pass

