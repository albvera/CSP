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
Assumes the nodes have unique ID attribute 0,1,...,n-1
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
	bar = progressbar.ProgressBar()
	print 'Creating labels'
	for v in bar(G.nodes()):		
		for reverse in range(0,2):								
			if objectives[reverse]!= None and v not in objectives[reverse]:
				continue									# v is not an objective (source or target)		
					
			hub,_ = ch_search(G,v,reverse)					# hub is a dict, keys are nodes visited in the search	
			# create label by storing in increasing ID 
			N[reverse][v] = len(hub)
			I[reverse][v] = sorted({G.node[k]['ID'] for k in hub.keys()})
			D[reverse][v] = []
			for j in xrange(0,N[reverse][v]):			
				w = Id_map[I[reverse][v][j]]
				D[reverse][v].append(hub[w])					# get distance to key			
	return(I,D,N)


"""
Prune labels by bootstrapping hub labels
G is the pruned augmented graph
Not only removes nodes with incorrect label, but also those who are not efficient
Id_map[Id] returns the node with that ID
"""
def prune_labels_bootstrap(I,D,N,Id_map,G):		
	print 'Prunning labels'
	for reverse in range(0,2):
		print 'Prunning hubs reverse={}'.format(reverse)
		bar = progressbar.ProgressBar()
		for v in bar(I[reverse].keys()):								# prune the hub of node v
			j = 0
			while j<N[reverse][v]:
				dist = 0
				w = Id_map[I[reverse][v][j]]					# j-th node in the hub
				if reverse == 0 and v!=w:						# if (w,x) not a sink-node, compute SP (v,b-x)->(w,0)
					dist = hl_query_pruned(I,D,v[0],w[0],v[1]-w[1])
				if reverse == 1 and v!=w:						# dist wv and (v,b) is a sink node
					dist = hl_query_pruned(I,D,w[0],v[0],w[1])
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
def prune_labels_dijkstra(I,D,N,Id_map,G):		
	#TODO: not working, need to run a reverse dijstra from the terminals instead
	print 'Prunning labels'
	for v in I[0].keys():
		lengths,_=nx.single_source_dijkstra(G,v,weight='dist')
		# prune forward hub of v
		j = 0
		while j<N[0][v]:
			w = Id_map[I[0][v][j]]					# j-th node in the hub
			dist = query_pruned(lengths,v[0],w[0],v[1]-w[1])
			if dist<D[0][v][j]:
				del I[0][v][j]
				del D[0][v][j]
				N[0][v]-=1
			else:
				j += 1

		# prune backward hubs containing v
		id_v = G.node[v]['ID']		
		for u in I[1].keys():
			if id_v not in I[1][u]:
				continue
			dist = query_pruned(lengths,v[0],u[0],v[1])
			j = I[1][u].index(id_v)
			if dist<D[1][u][j]:
				del I[1][u][j]
				del D[1][u][j]
				N[1][u]-=1
												 				
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
