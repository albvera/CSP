"""
Constructs contraction hierarchie graph by shortcutting online
Creates 'rank' attribute on nodes
Creates'shortcut' attribute on edges, takes value 0 or 1  
Node to shortcut is selected based on degree
Receives a directed graph
"""
import math, networkx as nx
def contract(G):	
	H = G.copy()
	nx.set_edge_attributes(G, 'shortcut', 0)		#original edges are not shortcuts
	for i in xrange(1,G.number_of_nodes()+1):		#set ranks 1,2,...,n
		degs = H.degree()									#obtain the degrees
		v = min(degs, key=degs.get)					#v is node with smallest degree
		for u in H.predecessors(v):				
			for w in H.successors(v):					#if P(u,w)=uvw and (u,w) is not an edge, then add shortcut
				if u!=w and not H.has_edge(u,w) and v in nx.shortest_path(H,u,w,weight='dist'):	
					H.add_edge(u,w)
					G.add_edge(u,w)
					G[u][w]['shortcut'] = 1
					G[u][w]['dist'] = H[u][w]['dist'] = H[u][v]['dist']+H[v][w]['dist']
		H.remove_node(v)	
		G.node[v]['rank'] = i


"""
Creates hub labels based on hierarchies
The hubs are three-tuples: N(v),I(v),D(v)
N(v)=#items in hub, I(v)=array with id's in hub, D(v) = array with distances
D(v)[k] = dist(v,I(v)[k]) for k=0,...,N(v)-1
I(v) is sorted in increasing order
Assumes the nodes are labeled 0,1,...,n-1
Each three-tuple can be reversed (1) or not reversed (0)
"""
from array import array

def createlabels(G):
	#I[0] is an dictionary for forward, I[0][v] is an array of ints with the id's of nodes in hubforward(v)
	I = {}	
	I[0] = I[1] = {}
	#D[0] is an dictionary for forward, D[0][v] is an array of floats with distances from node to hub			
	D = {}		
	D[0] = D[1] = {}
	n = nx.number_of_nodes(G)
	N = {}	
	N[0] = array('i',(0,)*n)			#array of n integers, sizes of forward hubs
	N[1] = array('i',(0,)*n)			#sizes of reversed hubs
	epsilon = 0.01							#to control floating point error when prunning
	for v in xrange(0,n):		
		for reverse in range(0,2):		#for reverse=0,1			
			#CH search to identify potential nodes in hub		
			hub = {}
			Dist,_ = CHsearch(G,v,reverse)
			#prune nodes in hub; only add nodes with correct
			for w in Dist:				
				if Dist[w] <= SPlength(G,v,w,reverse) + epsilon :		
					hub[w] = Dist[w]
		
			#Now create hub labels		
			N[reverse][v] = len(hub)
			I[reverse][v] = (array('i',(0,)*N[reverse][v]))
			D[reverse][v] = (array('f',(0,)*N[reverse][v]))
			#create label in increasing id	
			for i in xrange(0,N[reverse][v]):
				key = min(hub.keys())								#get smallest key/id
				I[reverse][v][i] = key				
				D[reverse][v][i] = hub[key]						#get distance to key			
				hub.pop(key,None)										#remove key from dict
	return(I,D,N)

"""
Runs a query using hub labels
Receives a forward and a backward hub
Nf, Nb are integers
Df, Db are arrays of floats 
If, Ib are arrays of id's
"""
def lengthquery(If,Df,Ib,Db):
	d = float("inf")	
	i = 0
	j = 0
	Nf = len(If)
	Nb = len(Ib)
	while i<Nf and i<Nb:
		if If[i]==Ib[j]:
			d = min(d,Df[i]+Db[j])
			i = i+1
			j = j+1
			continue
		if If[i]<Ib[j]:
			i = i+1
			continue
		j = j+1
	return d
				 

"""
Runs a forward search to all vertices using contraction hierarchies
Find shortest paths from the start vertex to all
vertices nearer than or equal to the end.
The output is a pair (D,P) where D[v] is the distance
from start to v and P[v] is the predecessor of v along
the shortest path from s to v.

NOT WORKING FOR SOME REASON

from priodict import priorityDictionary
def CHsearch(G,start,reverse):
	D = {}								# dictionary of final distances
	P = {}								# dictionary of predecessors
	Q = priorityDictionary()   	# estimated distances of non-final vert.
	Q[start] = 0
	
	for v in Q:
		D[v] = Q[v]
		N = (w for w in neighbours(G,v,reverse) if G.node[w]['rank'] > G.node[v]['rank'] ) 	#neighbours of v with higher rank
		for w in N:		
			vwLength = D[v] + dist(G,v,w,reverse)
			if w not in Q or vwLength < Q[w]:
				Q[w] = vwLength
				P[w] = v
	return (D,P)
"""

def CHsearch(G, s, reverse):
	visited = {s: 0}			#distances of visited nodes
	path = {}
	nodes = G.nodes()

	while nodes: 
		min_node = None
		for v in nodes:
			if v in visited:
				if min_node is None:
					min_node = v
				elif visited[v] < visited[min_node]:
					min_node = v
		
		if min_node is None:
			break
		nodes.remove(min_node)
		current_weight = visited[min_node]

		for w in neighbours(G,min_node,reverse):
			if G.node[w]['rank'] < G.node[min_node]['rank']:
				continue
			weight = current_weight + dist(G,min_node,w,reverse)
			if w not in visited or weight < visited[w]:
				visited[w] = weight
				path[w] = min_node

  	return visited, path

"""
Runs a length query from s to t using CH
"""
def CHquery(G,s,t):
	Df,_ = CHsearch2(G,s,0)		#forward search from s
	Db,_ = CHsearch2(G,t,1)		#backward search from t
	dist = float("inf")
	for u in Df.keys():
		if u in Db and Df[u]+Db[u]<dist:
			dist = Df[u]+Db[u]
	return dist

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




