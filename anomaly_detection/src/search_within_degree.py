from collections import deque

class Search():
	def __init__(self, G, search_degree, source):
		self.search_degree = int(search_degree)
		self.source_vertex = source
		self.marked = {}
		self.distTo = {}
		self.edgeTo = {}

		for key in G.keys():
			self.marked[key] = False
			self.distTo[key] = float('inf')
			self.edgeTo[key] = None

		self.bfs(G, source)

	def bfs(self, G, source_vertex):
		queue = deque()

		self.distTo[source_vertex] = 0
		self.marked[source_vertex] = True

		queue.append(source_vertex)

		while queue:
			current = queue.popleft()

			friends = G[current].get_friends()
			for friend in friends:
				if not self.marked[friend] and self.distTo[current] + 1 <= self.search_degree:
					self.edgeTo[friend] = current
					self.distTo[friend] = self.distTo[current] + 1
					self.marked[friend] = True
					queue.append(friend)

	def get_friends_within_degree(self):
		valid_friends_list = []
		for friend in self.distTo.keys():
			if self.distTo[friend] <= self.search_degree and friend != self.source_vertex:
				valid_friends_list.append(friend)

		return valid_friends_list

