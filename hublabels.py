import networkx as nx
from graphinfo import *
from CH import *

"""
Creates hub labels based on hierarchies
The hubs are three-tuples: N(v),I(v),D(v)
N(v)=#items in hub, I(v)=array with id's in hub, D(v) = array with distances
D(v)[k] = dist(v,I(v)[k]) for k=0,...,N(v)-1
I(v) is sorted in increasing order
Each three-tuple can be reversed (1) or not reversed (0)
Assumes the nodes have unique ID attribute 0,1,...,n-1
If targets is specified, only computes backward hubs for targets
If sources is specified, only computes forward hubs for sources
"""
from array import array

def createlabels(G,sources = None, targets = None):
	#I[0] is an dictionary for forward, I[0][v] is an array of ints with the id's of nodes in hubforward(v)
	I = {}	
	I[0] = I[1] = {}
	#D[0] is an dictionary for forward, D[0][v] is an array of floats with distances from node to hub			
	D = {}		
	D[0] = D[1] = {}
	n = nx.number_of_nodes(G)
	N = {}	
	N[0] = {}							#NO LONGER ARRAY, sizes of forward hubs
	N[1] = {}							#sizes of reversed hubs
	objectives = {}					#only works if sources or targets are specified
	objectives[0] = sources
	objectives[1] = targets
	for v in G.nodes():		
		for reverse in range(0,2):		#for reverse=0,1		
			if objectives[0]!= None and v not in objectives[0]:
				continue						#v is not an objective (source or target)
			#CH search to identify potential nodes in hub		
			hub = {}
			Dist,_ = CHsearch(G,v,reverse)
			#prune nodes in hub; only add nodes with correct
			for w in Dist:				
				if Dist[w] <= SPlength(G,v,w,reverse):		
					hub[w] = Dist[w]
		
			#Now create hub labels		
			N[reverse][v] = len(hub)
			I[reverse][v] = (array('i',(0,)*N[reverse][v]))
			D[reverse][v] = (array('f',(0,)*N[reverse][v]))
			#Obtain dictionary with ids, but only of those nodes in the hub	
			temp = {k: nx.get_node_attributes(G,'ID')[k] for k in hub.keys()}
			#create label in increasing ID
			for i in xrange(0,N[reverse][v]):
				k = min(temp, key = temp.get)						#get key with smallest ID
				I[reverse][v][i] = temp[k]				
				D[reverse][v][i] = hub[k]							#get distance to key			
				temp.pop(k,None)										#remove key from dict
	return(I,D,N)

"""
Runs a query using hub labels
Receives a forward and a backward hub
Nf, Nb are integers
Df, Db are arrays of floats 
If, Ib are arrays of id's
"""
def HLquery(If,Df,Ib,Db):
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
				 


