"""
Constructs contraction hierarchie graph by shortcutting online
Creates 'rank' attribute on nodes
Creates'shortcut' attribute on edges, takes value 0 or 1  
Node to shortcut is selected based on degree
Receives a directed graph
"""
import math, networkx as nx
from graphinfo import *

def contract(G):	
	H = G.copy()
	nx.set_edge_attributes(G, 'shortcut', 0)		#original edges are not shortcuts
	n = G.number_of_nodes()
	for i in xrange(1,n):							#set ranks 1,2,...,n-1
		degs = H.degree()							#obtain the degrees
		v = min(degs, key=degs.get)					#v is node with smallest degree
		new_edges = shortcut(H,v)
		for (u,w) in new_edges:				
			H.add_edge(u,w)
			G.add_edge(u,w)
			G[u][w]['shortcut'] = 1
			G[u][w]['dist'] = H[u][w]['dist'] = H[u][v]['dist']+H[v][w]['dist']
		H.remove_node(v)	
		G.node[v]['rank'] = i
	#There is just one node remaining in H
	v = H.nodes()[0]
	G.node[v]['rank'] = n

"""
Constructs contraction hierarchie
Selects node to contract using a score(v) = #edges added if v were shortcut - #edges removed if v were shortcut (=degreee)
"""
def contractscore(G):	
	H = G.copy()
	nx.set_edge_attributes(G, 'shortcut', 0)		#original edges are not shortcuts
	n = G.number_of_nodes()
	for i in xrange(1,n):							#set ranks 1,2,...,n-1
		min_score = float("inf")		
		min_node = None								#node with minimum score
		min_edges = []								#edges added by min_node
		degs = H.degree()
		#Compute node with lowest score
		for v in H.nodes():
			added = shortcut(H,v)					#edges added if v were shurtcut
			if min_score > len(added)-degs[v]:		#v has the lowest score
				min_node = v
				min_edges = list(added)				#copy edges
				min_score = len(added)-degs[v]

		#Now min_node will be contracted
		for (u,w) in min_edges:
			H.add_edge(u,w)
			G.add_edge(u,w)
			G[u][w]['shortcut'] = 1
			G[u][w]['dist'] = H[u][w]['dist'] = H[u][min_node]['dist']+H[min_node][w]['dist']
		H.remove_node(min_node)	
		G.node[min_node]['rank'] = i
	#There is just one node remaining in H
	v = H.nodes()[0]
	G.node[v]['rank'] = n

"""
Uses shortest path covers to contract
Adds nodes greedily to a cover C and then contract in reverse order
"""
def contractSPC(G):
	nx.set_edge_attributes(G, 'shortcut', 0)		#original edges are not shortcuts
	C = []	
	n = G.number_of_nodes()
	H = G.copy()
	i = n
	while i >=2:
		h = dict.fromkeys(H.nodes(),0)	#h[v] is the number of paths hit by v 
		for r in H.nodes():				#search all the paths starting at root r
			path=nx.single_source_dijkstra_path(H, r, None, weight='dist')	
			for t in path.keys():		#for all diferent nodes reached by r		
				for u in path[t]:		#for all nodes in (r,t)-path 
					h[u] = h[u] + 1		#u hits an additional path
				
		v = max(h, key=h.get)			#v is node hitting more paths
		G.node[v]['rank'] = i			
		i = i-1
		H.remove_node(v)
		C.append(v)	
	#There is just one node remaining in H
	v = H.nodes()[0]
	G.node[v]['rank'] = 1
	C.append(v)

	#Now we contract in the reverse order of C
	i = n-1
	H = G.copy()
	while i >=1:						#for C[n-1],C[n-2],...,C[1]. Node C[0] is not contracted
		v = C[i] 						#v is to be contracted
		new_edges = shortcut(H,v)
		for (u,w) in new_edges:				
			H.add_edge(u,w)
			G.add_edge(u,w)
			G[u][w]['shortcut'] = 1
			G[u][w]['dist'] = H[u][w]['dist'] = H[u][v]['dist']+H[v][w]['dist']
		H.remove_node(v)	
		i = i-1
	
	

"""
Shortcuts node v and returns edges that must be added to the graph
"""
def shortcut(H,v):
	sucs = H.edges(v,'dist')					#Succesors of v. It's a triplet (v,w,dist(v,w))
	if not sucs:									#v has no successors 
		return []
	sucs = zip(*sucs)								#Now sucs[1] has succesors of v, succs[2] has distances
	maxvw = max(sucs[2])							#max edge length outgoing from v 
	new_edges = []
	for u in H.predecessors(v):				
		#Obtain the shortest paths from u. Use maxvw to prune the search
		path=nx.single_source_dijkstra_path(H, u, maxvw + H[u][v]['dist'], weight='dist')	
		for w in sucs[1]:				#if P(u,w)=uvw and (u,w) is not an edge, then add shortcut
			if u!=w and not H.has_edge(u,w) and v in path[w]:	
				new_edges.append((u,w))
	return new_edges
"""
Runs a CH search, visiting all nodes with higher rank
The output is a pair (D,P) where D[v] is the distance from start to v and P[v] is the predecessor of v along the shortest path from s to v.
One can specify cutoff (only paths of length <= cutoff are returned) and target.
"""
from collections import deque
from heapq import heappush, heappop
from itertools import count

def CHsearch(G, source, reverse, target=None, cutoff=None):
	if source == target:
		return ({source: 0}, {source: [source]})
	push = heappush
	pop = heappop
	D = {}  								# dictionary of final distances
	paths = {source: [source]}  	# dictionary of paths
	seen = {source: 0}
	c = count()
	fringe = []  						# use heapq with (distance,label) tuples
	push(fringe, (0, next(c), source))
	while fringe:
		(d, _, v) = pop(fringe)
		if v in D:
			continue  					# already searched this node.
		D[v] = d
		if v == target:
			break
		N = neighbours(G,v,reverse)
		for w in N:
			if G.node[w]['rank']<G.node[v]['rank']:
				continue	
			vw_dist = D[v] + dist(G,v,w,reverse)
			if cutoff is not None:
				if vw_dist > cutoff:
					continue
			if w not in seen or vw_dist < seen[w]:
				seen[w] = vw_dist
				push(fringe, (vw_dist, next(c), w))
				paths[w] = paths[v] + [w]
	return (D, paths)

"""
Runs a length query from s to t using CH
"""
def CHquery(G,s,t):
	Df,_ = CHsearch(G,s,0)		#forward search from s
	Db,_ = CHsearch(G,t,1)		#backward search from t
	dist = float("inf")
	for u in Df.keys():
		if u in Db and Df[u]+Db[u]<dist:
			dist = Df[u]+Db[u]
	return dist

