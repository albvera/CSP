"""
Receives a digraph and generates k unit costs randomly
Each of the k unit costs is asigned at a random edge
The edges are selected without replacement
Creates label 'cost' and overrides any pre-existing costs
"""
import random, networkx as nx
import time, progressbar

def randcost(G,k):
	nx.set_edge_attributes(G, 'cost', 0)		#set all costs to 0
	edges = random.sample(G.edges(),k)			#obtain k edges
	dic = {key: 1 for key in edges}				#dictionary, the k edges have cost 1
	nx.set_edge_attributes(G, 'cost', dic)		#set unit cost for k edges
		

"""
Returns expanded digraph
Receives a graph or digraph and budget B
Assumes a label 'cost' on edges and nodes of G are 0,1,2,...,n-1
The nodes are (u,b), u=0,...,n-1 and b=0,...,B
If omit_sink=True, it doesn't add the sink nodes (u,-1)
A unique ID is created by: (0,B) ->1, (1,B) ->2,..., (n-1,B)->n-1, (0,B-1)->n and so on 
"""
from graph_info import *
import itertools, math
def augment(G,B,omit_sink=None):
	H = nx.DiGraph()
	nodes = list(itertools.product(G.nodes(),range(0,B+1)))
	if not omit_sink:
		nodes = nodes + [(u,-1) for u in G.nodes()]
	H.add_nodes_from(nodes)
	#create the edges
	i = 0
	b = B
	while b>=0:
		for u in G.nodes():
			H.node[(u,b)]['ID'] = i
			N = neighbours(G,u,0)								# forward neighbours of u
			for v in N:								
				if G[u][v]['cost']<=b:
					b2 = b-G[u][v]['cost']
					H.add_edge((u,b),(v,b2))
					H[(u,b)][(v,b2)]['dist'] = G[u][v]['dist']
			if not omit_sink:			
				d = float(round(math.log(2-b/B),4))				# d decreasing in b and less than 1
				H.add_edge((u,b),(u,-1),dist=d)	
			i = i+1
		b = b-1

	if omit_sink:	
		return H
	
	#Now assing ID for sink nodes
	for u in G.nodes():
		H.node[(u,-1)]['ID'] = i
		i = i+1
	return H

"""
Receives original graph G and augmented graph GB
"""
from sets import Set
def prune_augmented(G,B):
	print 'Prunning augmented graph'
	bar = progressbar.ProgressBar()
	H = nx.DiGraph()
	GB = augment(G,B,omit_sink=True)
	edges = Set()											# keep track of added edges as 4-tuples
	for s in bar(G.nodes()):
		lengths,paths=nx.single_source_dijkstra(GB,(s,B),weight='dist')			
		for t in G.nodes():
			if t==s:
				continue
			dist = [float("inf")]*(B+1)						# dist[b] = distance with budget b
			for x in xrange(B,-1,-1):
				if (t,x) not in lengths:
					if x<B:
						dist[B-x] = dist[B-x-1]
					continue		
				if x==B or lengths[(t,x)]<dist[B-x-1]:		# path is strictly better than the previous
					path_tx = paths[(t,x)]
					len_p = len(path_tx)				
					l = 0
					while l<=len_p-2:						# last node in the path is sink, don't count it
						(u,y) = path_tx[l]
						(v,z) = path_tx[l+1] 
						if (u,y-x,v,z-x) not in edges:
							edges.add((u,y-x,v,z-x))
							H.add_edge((u,y-x),(v,z-x),dist=G[u][v]['dist'])
						l += 1
				else:
					dist[B-x] = dist[B-x-1]
	# assing ID
	i = 0
	for u in H.nodes():
		H.node[u]['ID'] = i
		i = i+1

	return H

"""
Receives lengths of paths in the prunned graph G, source, target and budget
"""
def query_prunned(lengths,s,t,b):
	#TODO: not working, need to explore source instead of target
	if s == t:
		return 0
	dist = float("inf")
	for x in range(b,-1,-1):
		if (t,x) not in lengths:
			continue
		d = lengths[(t,x)]
		if d<dist:
			dist = d
	return dist	
