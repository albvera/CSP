import networkx as nx
from graph_info import *
from ch import *
from costs import *
import time, progressbar

"""
Creates hub labels based on hierarchies
The hubs are three-tuples: N(v),I(v),D(v)
N(v)=#items in hub, I(v)=array with id's in hub, D(v) = array with distances
D(v)[k] = dist(v,I(v)[k]) for k=0,...,N(v)-1
I(v) is sorted in increasing order
Each three-tuple can be backward (reverse=1) or forward (reversed=0)
Assumes the nodes have unique ID attribute
List of targets (backward hubs) and sources (forward hubs) can be specified
"""
from array import array

def create_labels(G,Id_map,sources = None, targets = None):
	#I[0] is an dictionary for forward, I[0][v] is an array with the id's of nodes in hubforward(v)
	I = {}	
	I[0] = {}
	I[1] = {}
	#D[0] is an dictionary for forward, D[0][v] is an array of distances from node to hub			
	D = {}		
	D[0] = {}
	D[1] = {}
	N = {}	
	N[0] = {}												# sizes of forward hubs
	N[1] = {}												# sizes of reversed hubs
	objectives = {}											# used to work with sources or targets
	objectives[0] = sources
	objectives[1] = targets
	rank = nx.get_node_attributes(G,'rank')
	ID = nx.get_node_attributes(G,'ID')
	bar = progressbar.ProgressBar()
	print 'Creating labels'
	for v in bar(G.nodes()):		
		for reverse in range(0,2):								
			if objectives[reverse]!= None and v not in objectives[reverse]:
				continue									# v is not an objective (source or target)		
					
			hub,_ = ch_search(G,v,reverse,rank)				# hub is a dict, keys are nodes visited in the search	
			# create label by storing in increasing ID 
			N[reverse][v] = len(hub)
			I[reverse][v] = sorted({ID[k] for k in hub.keys()})
			D[reverse][v] = []
			for i in I[reverse][v]:			
				w = Id_map[i]
				D[reverse][v].append(hub[w])				# get distance to key			
	return(I,D,N)


"""
Prune labels by bootstrapping hub labels
G is the pruned augmented graph
Not only removes nodes with incorrect label, but also those who are not efficient
Id_map[Id] returns the node with that ID
"""
import operator
def prune_labels_bootstrap(I,D,N,Id_map,G):		
	#query = hl_query_extra_edges 
	query = hl_query_pruned
	keys = {}
	keys[1] = I[1].keys()
	keys[0] = I[0].keys()
	keys[0].sort(key=operator.itemgetter(1))					# order nodes by ascending budget
	for reverse in range(1,-1,-1):
		if reverse == 1:
			print 'Pruning backward hubs'
		else:
			print 'Pruning forward hubs'
		bar = progressbar.ProgressBar()
		for v in bar(keys[reverse]):							# prune the hub of node v
			j = 0
			while j<N[reverse][v]:
				dist = 0
				w = Id_map[I[reverse][v][j]]					# j-th node in the hub
				if reverse == 0 and v!=w:						# if (w,x) not a sink-node, compute SP (v,b-x)->(w,0)
					dist = query(I,D,v[0],w[0],v[1]-w[1])
				if reverse == 1 and v!=w:						# dist wv and (v,b) is a sink node
					dist = query(I,D,w[0],v[0],w[1])
				if dist<D[reverse][v][j]:
					del I[reverse][v][j]
					del D[reverse][v][j]
					N[reverse][v]-=1
				else:
					j+=1
"""
Prune labels of not augmented graph
"""
def prune_labels_regular(I,D,N,Id_map):		
	for reverse in range(1,-1,-1):
		if reverse == 1:
			print 'Pruning backward hubs'
		else:
			print 'Pruning forward hubs'
		bar = progressbar.ProgressBar()
		for v in I[reverse].keys():								# prune the hub of node v
			j = 0
			while j<N[reverse][v]:
				dist = 0
				w = Id_map[I[reverse][v][j]]					# j-th node in the hub
				if reverse == 0 and v!=w:						
					dist = hl_query(I[0][v],D[0][v],I[1][w],D[1][w])
				if reverse == 1 and v!=w:						
					dist = hl_query(I[0][w],D[0][w],I[1][v],D[1][v])
				if dist<D[reverse][v][j]:
					del I[reverse][v][j]
					del D[reverse][v][j]
					N[reverse][v]-=1
				else:
					j = j+1


"""
Prune labels using Dijkstra, removes also inefficient nodes
G is the pruned augmented graph 
"""
def prune_labels_dijkstra(I,D,N,Id_map,G,nodes,B):		
	G.reverse(copy=False)
	dijkstra = nx.single_source_dijkstra
	contains_target = {}
	for t in nodes:
		contains_target[t] = Set()

	for v in I[0].keys():
		for i in I[0][v]:
			contains_target[Id_map[i][0]].add(v)				# can add the budget of (t,x) to save time in the loop
		
	for t in nodes:
		lengths,_=dijkstra(G,(t,0),weight='dist')		
		dist = {}												# dist[s][b] = dist(s,t|b)
		sources = Set([Id_map[i][0] for i in I[1][(t,0)]])		# s such that (s,b) is in the hub		
		for s in sources:
			add_distances(dist,s,t,lengths)
		j = 0
		while j<N[1][(t,0)]:
			(s,b) = Id_map[I[1][(t,0)][j]]						# j-th node in the hub
			if dist[s][b]<D[1][(t,0)][j]:
				del I[1][(t,0)][j]
				del D[1][(t,0)][j]
				N[1][(t,0)]-=1
			else:
				j = j+1
		
		for (s,b) in contains_target[t]:
			if s not in sources:
				add_distances(dist,s,t,lengths)
				sources.add(s)
			j = 0
			while j<N[0][(s,b)]:
				(v,x) = Id_map[I[0][(s,b)][j]]						# j-th node in the hub
				if v!=t or D[0][(s,b)][j] == dist[s][b-x]:
					j += 1
				else:
					del I[0][(s,b)][j]
					del D[0][(s,b)][j]
					N[0][(s,b)]-=1

def add_distances(dist,s,t,lengths):
	if t == s:
		dist[t] = [0]*(B+1)
		return
	dist[s] = [float("inf")]*(B+1)
	if (s,0) in lengths:
		dist[s][0] = lengths[(s,0)]
	for b in xrange(1,B+1):
		if (s,b) not in lengths or lengths[(s,b)]>=dist[s][b-1]:
			dist[s][b] = dist[s][b-1]
			continue		
		dist[s][b] = lengths[(s,b)]
												 				
"""
Runs a query using hub labels
Receives a forward and a backward hub
Nf, Nb are integers
Df, Db are arrays of floats 
If, Ib are arrays of id's
"""
def hl_query(If,Df,Ib,Db):
	d = float("inf")	
	i = 0
	j = 0
	Nf = len(If)
	Nb = len(Ib)
	while i<Nf and j<Nb:
		if If[i]==Ib[j]:
			if Df[i]+Db[j] < d:
				d = Df[i]+Db[j]
			i = i+1
			j = j+1
		elif If[i]<Ib[j]:
			i = i+1
		else:
			j = j+1
	return d

"""
Receives hubs for pruned augmented graph, source, target and budget
"""
def hl_query_pruned(I,D,s,t,b):
	if s == t:
		return 0
	if (t,0) not in I[1]:
		return float("inf")
	dist = float("inf")
	for x in range(b,-1,-1):
		if (s,x) not in I[0]:
			continue
		d = hl_query(I[0][(s,x)],D[0][(s,x)],I[1][(t,0)],D[1][(t,0)])
		if d<dist:
			dist = d
	return dist	

"""
Receives hubs for pruned augmented graph, source and target
Returns all the efficient distances to s
"""
def hl_query_frontier(I,D,s,t,B):
	if s == t:
		return [0]*(B+1)
	if (t,0) not in I[1]:
		return [float("inf")]*(B+1)	
	dist = [float("inf")]*(B+1)
	if (s,0) in I[0]:
		dist[0] = hl_query(I[0][(s,0)],D[0][(s,0)],I[1][(t,0)],D[1][(t,0)])
	for b in range(1,B+1):
		if (s,b) not in I[0]:
			dist[b] = dist[b-1]
			continue
		d = hl_query(I[0][(s,b)],D[0][(s,b)],I[1][(t,0)],D[1][(t,0)])
		if d<dist[b-1]:
			dist[b] = d
		else:
			dist[b] = dist[b-1]
	return dist		

"""
Receives hubs for pruned augmented graph with extra edges (v,b)->(v,b-1), source, target and budget
"""
def hl_query_extra_edges(I,D,s,t,b):
	if s == t:
		return 0
	return hl_query(I[0][(s,b)],D[0][(s,b)],I[1][(t,0)],D[1][(t,0)])

"""
Save labels already constructed
"""
import pickle
def write_labels(I,D,N,name):
	with open(name, "wb") as f:
		pickle.dump({'IDs':I, 'Dist':D, 'Size': N}, f)

"""
Read labels from file and return I,D
"""
def read_labels(name):
	with open(name, "rb") as f:
		dic = pickle.load(f)
	return dic['IDs'], dic['Dist'], dic['Size']
