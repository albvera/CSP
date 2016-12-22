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
	H = nx.DiGraph()
	n = G.number_of_nodes()
	nodes = list(itertools.product(range(0,n),range(-1,B+1)))
	H.add_nodes_from(nodes)
	#create the edges
	i = 0
	b = B
	while b>=0:
		for u in xrange(0,n):
			H.node[(u,b)]['ID'] = i
			for v in neighbours(G,u,0):		#forward neighbours of u	
				if G[u][v]['cost']<=b:
					b2 = b-G[u][v]['cost']
					H.add_edge((u,b),(v,b2))
					H[(u,b)][(v,b2)]['dist'] = G[u][v]['dist']
			d = math.log(2-b/B)					#d decreasing in b and less than 1
			H.add_edge((u,b),(u,-1),dist=round(d,3))	
			i = i+1
		b = b-1
	
	#Now assing ID for sink nodes
	for u in xrange(0,n):
		H.node[(u,-1)]['ID'] = i
		i = i+1
	return H
