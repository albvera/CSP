"""
Receives a digraph and generates k unit costs randomly
Each of the k unit costs is asigned at a random edge
The edges are selected without replacement
Creates label 'cost' and overrides any pre-existing costs
"""
import random, networkx as nx

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
A unique ID is created by: (0,B) ->1, (1,B) ->2,..., (n-1,B)->n-1, (0,B-1)->n and so on 
"""

from graph_info import *
import itertools, math
def augment(G,B):
	print 'Augmenting graph'
	H = nx.DiGraph()
	nodes = list(itertools.product(G.nodes(),range(-1,B+1)))
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
			d = float(round(math.log(2-b/B),4))					# d decreasing in b and less than 1
			H.add_edge((u,b),(u,-1),dist=d)	
			i = i+1
		b = b-1
	
	#Now assing ID for sink nodes
	for u in G.nodes():
		H.node[(u,-1)]['ID'] = i
		i = i+1
	return H

"""
Receives original graph G and augmented graph GB
"""
def prune_augmented(G,GB,B):
	print 'Prunning augmented graph'
	H = nx.DiGraph()
	
	for s in G.nodes():
		for b in xrange(0,B+1):
			paths=nx.single_source_dijkstra_path(GB,(s,b),weight='dist')
			for t in G.nodes():
				if (t,-1) not in paths or t == s:
					continue
				len_p = len(paths[(t,-1)])				
				if paths[(t,-1)][len_p-2][1]!=0:				# path didn't consume all the budget
					continue
				l = 0
				while l<=len_p-3:								# last node in the path is sink, don't count it
					(u,x) = paths[(t,-1)][l]
					(v,y) = paths[(t,-1)][l+1] 
					H.add_edge((u,x),(v,y),dist=G[u][v]['dist'])
					l = l+1

	# assing ID
	i = 0
	for u in H.nodes():
		H.node[u]['ID'] = i
		i = i+1

	return H

"""
Receives prunned augmented graph G, source, target and budget
"""
def query_prunned(G,s,t,b):
	dist = float("inf")
	for x in range(b,-1,-1):
		if (s,x) not in G.nodes():
			continue
		length,path = nx.single_source_dijkstra(G,(s,x),target=(t,0),weight='dist')
		if (t,0) not in length or length[(t,0)]>dist:
			continue
		dist = length[(t,0)]
	return dist	
