import networkx as nx
from graph_info import *
from ch import *

"""
Creates hub labels based on hierarchies
The hubs are three-tuples: N(v),I(v),D(v)
N(v)=#items in hub, I(v)=array with id's in hub, D(v) = array with distances
D(v)[k] = dist(v,I(v)[k]) for k=0,...,N(v)-1
I(v) is sorted in increasing order
Each three-tuple can be reversed (1) or not reversed (0)
Assumes the nodes have unique ID attribute 0,1,...,n-1
If a list of targets is specified, only computes backward hubs for targets
If a list of sources is specified, only computes forward hubs for sources
"""
from array import array

def create_labels(G,Paths,sources = None, targets = None):
	#I[0] is an dictionary for forward, I[0][v] is an array of ints with the id's of nodes in hubforward(v)
	I = {}	
	I[0] = {}
	I[1] = {}
	#D[0] is an dictionary for forward, D[0][v] is an array of floats with distances from node to hub			
	D = {}		
	D[0] = {}
	D[1] = {}
	n = nx.number_of_nodes(G)
	N = {}	
	N[0] = {}							#sizes of forward hubs
	N[1] = {}							#sizes of reversed hubs
	objectives = {}						#does something only if sources or targets are specified
	objectives[0] = sources
	objectives[1] = targets
	for v in G.nodes():		
		for reverse in range(0,2):							#for reverse=0,1	
			if objectives[reverse]!= None and v not in objectives[reverse]:
				continue									#v is not an objective (source or target)
			#CH search to identify potential nodes in hub		
			hub = {}
			Dist,_ = ch_search(G,v,reverse)
			#prune nodes in hub; only add nodes with correct distance
			for w in Dist.keys():
				l = path_length(v,w,Paths,G,reverse)		
				if Dist[w] <= l:		
					hub[w] = Dist[w]	
		
			#Now create hub labels		
			N[reverse][v] = len(hub)
			I[reverse][v] = []
			D[reverse][v] = []
			#Obtain dictionary with ids, but only of those nodes in the hub	
			temp = {k: G.node[k]['ID'] for k in hub.keys()}
			#create label in increasing ID
			while temp:
				w = min(temp, key = temp.get)					#get node with smallest ID
				I[reverse][v].append(temp[w])				
				D[reverse][v].append(hub[w])					#get distance to key			
				temp.pop(w,None)								#remove key from dict
	return(I,D,N)

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
			d = min(d,Df[i]+Db[j])
			i = i+1
			j = j+1
		elif If[i]<Ib[j]:
			i = i+1
		else:
			j = j+1
	return d

"""
Compute path length from v to w if reverse = 0 or from w to v if reverse=1
"""
def path_length(v,w,Paths,G,reverse):
	path = []
	if reverse == 0:
		if w not in Paths[v]:				# w not reached by v
			return float("inf")
		path = Paths[v][w]
	else:
		if v not in Paths[w]:
			return float("inf")
		path = Paths[w][v] 

	if len(path) == 1:
		return 0
	l = 0
	i = 0
	while i<len(path)-1:
		l = l + G[path[i]][path[i+1]]['dist']
		i = i+1
	return l
	

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
