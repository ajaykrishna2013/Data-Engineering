from collections import deque

class User():
	def __init__(self, id, T=2):
		self.user_id = id
		self.tracked = T
		self.friends = deque()
		self.purchases = deque()

	def add_purchase(self, p):
		if len(self.purchases) == self.tracked:
			drop = self.purchases.get()
		self.purchases.append(p)

	def get_purchases(self):
		return self.purchases

	def get_userid(self):
		return self.user_id

	def add_friend(self, friend_id):
		self.friends.append(friend_id)

	def remove_friend(self, friend_id):
		friend_index = list(self.friends).index(friend_id)
		del self.friends[friend_index]

	def get_friends(self):
		return self.friends

	def get_degree(self):
		return len(self.friends)




if __name__ =='__main__':
	q = Queue()

