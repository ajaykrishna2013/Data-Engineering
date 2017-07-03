from collections import deque
import logging

class User():
	def __init__(self, id, T=2):
		self.logger = logging.getLogger(__name__)
		#self.logger.setLevel(logging.DEBUG)
		# fh = logging.FileHandler('User.log')
		# fh.setLevel(logging.DEBUG)
		# self.logger.addHandler(fh)
		self.user_id = id
		self.tracked = T
		self.friends = deque()
		self.purchases = deque()
		self.logger.info('Creating user %s', self.user_id)

	def add_purchase(self, p):
		"""
		adds a purchase to a users purchase list. If the number of purchases
		has reached the number to be tracked, then pop from the front of the
		queue and add the new purchase to the back of the queue.
		Args:
		    p: purchase tuple (amoumt, timestamp, global count)

		Returns:

		"""
		if len(self.purchases) == self.tracked:
			drop = self.purchases.popleft()
		self.logger.info('Adding purchase %s for user %s', p, self.user_id)
		self.purchases.append(p)

	def get_num_tracked(self):
		return self.tracked

	def get_purchases(self):
		"""
		orders the purchases by timestamp before returning to caller
		Returns:

		"""
		ordered_purchases = sorted(self.purchases, key=lambda x: x[1])
		return ordered_purchases

	def get_userid(self):
		return self.user_id

	def add_friend(self, friend_id):
		"""
		Adds friend with friend_id to the friend list
		Args:
		    friend_id:

		Returns:

		"""
		self.logger.info('Adding friend %s for user %s', friend_id, self.user_id)
		self.friends.append(friend_id)

	def remove_friend(self, friend_id):
		"""
		removes a friend from the friend list
		Args:
		    friend_id:

		Returns:
			nothing
		"""
		friend_index = list(self.friends).index(friend_id)
		self.logger.info('Remove friend %s for user %s', self.friends[friend_index], self.user_id)
		del self.friends[friend_index]

	def get_friends(self):
		return self.friends

	def get_degree(self):
		return len(self.friends)


