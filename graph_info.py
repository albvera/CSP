import networkx as nx

def dist_forward(G,v,w):
	return G[v][w]['dist']

def dist_backward(G,v,w):
	return G[w][v]['dist']

"""
If reverse=1, returns predecessors of v
Otherwise, returns successors of v
Requires global variable is_direced
"""
def neighbours(G,v,reverse):
	if not nx.is_directed(G):
		return G.neighbors(v)
	if reverse == 1:
		return G.predecessors(v)
	else:
		return G.successors(v)

"""
Run Dijkstra to obtain all the lengths in the efficient frontier
Receives augmented graph without sink nodes, source, target and B
"""
def dijkstra_frontier(G,s,t,B):
	if t == s:
		return [0]*(B+1)
	lengths,_=nx.single_source_dijkstra(G,(s,B),weight='dist')			
	dist = [float("inf")]*(B+1)
	if (t,B) in lengths:
		dist[0] = lengths[(t,B)]
	for x in xrange(B-1,-1,-1):								# b = B-x
		if (t,x) not in lengths or lengths[(t,x)]>=dist[B-x-1]:
			dist[B-x] = dist[B-x-1]
			continue		
		dist[B-x] = lengths[(t,x)]
	return dist

"""
Receives augmented graph with sink nodes
Runs length query
"""
def dijkstra_sink(G,s,t,b):
	try:
		return int(nx.shortest_path_length(G,(s,b),(t,-1),weight='dist'))
	except:
		return float("inf")	#Nodes are not reachable

def dijkstra_length(G,s,t):
	try:
		return int(nx.shortest_path_length(G,s,t,weight='dist'))
	except:
		return float("inf")	#Nodes are not reachable
