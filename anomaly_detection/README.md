# High Level Design

## detect_anomaly.py
- has the main function
- calls 2 functions
    - one to process the batch_log and create the social network class with the
      D and T parameters.
    - one to process the stream_log and calls a check anomaly function on the
      social network for every purchase event

## social_network.py
- Has the SocialNetwork class, which is used above
- Maintains a network of users as a python dictionary
- has function to add a friend, remove a friend, check anomaly
- some of these function call functions on the user object
- the check_anomaly_update_network function further calls 2 helper functions
    - one creates a search object of type Search (explained below)
    - a check_anomaly function which detects an anomaly and writes to
      flagged_purchases.json
- the check_anomaly function gathers all the users returned from the search
  object and collects the purchases in the network. It then heapify's them and
  finds the newest T purchases. Uses numpy's built in mean and std functions to
  calculate the mean and standard deviation and checks against the threshold to
  flag an anomaly

## search_within_degree.py
- Has the Search class which has 2 main funcitons
    - one function does a breath first search from the source vertex while
      keeping track of distance from source vertex. If the distance is less
      than or equal to the search degree, it is marked as visited
    - a second function to find and return the nodes found by the bfs
      This function is used by the social_network class above

## users.py
- This is the class for the user object which has 2 main properties
- A queue of purchases and a list of friends
- The add purchase function tracks the size of the queue and pushes new transactions
- The add friend function adds a friend to the adjacency list of the user
- There is also a function for removing a friend from the adjacency list
- The SocialNetwork class calls the above mentioned utility functions to manipulate
  the user data.


# Additional libraries used
I have used numpy as an additional library outside of what comes with python 2.7.



