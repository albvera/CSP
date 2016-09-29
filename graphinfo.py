import networkx as nx
"""
Returns the distance of an edge dist(v,w)
If reverse=1, returns dist(w,v)
"""
def dist(G,v,w,reverse):
	if reverse == 1: 			#do reverse
		return G[w][v]['dist']
	else:
		return G[v][w]['dist']	#do not reverse 

"""
If reverse=1, returns predecessors of v
Otherwise, returns successors of v
"""
def neighbours(G,v,reverse):
	if not nx.is_directed(G):
		return G.neighbors(v)
	if reverse == 1:
		return G.predecessors(v)
	else:
		return G.successors(v)

"""
If reverse=1, returns predecessors shortest path length from w to v
Otherwise, returns shortest path length from v to w
"""
def SPlength(G,v,w,reverse):
	if reverse == 1:
		return nx.shortest_path_length(G,w,v,weight='dist')
	else:
		return nx.shortest_path_length(G,v,w,weight='dist')
