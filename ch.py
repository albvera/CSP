"""
Constructs contraction hierarchie graph by shortcutting online
Creates 'rank' attribute on nodes
Creates'shortcut' attribute on edges, takes value 0 or 1  
Node to shortcut is selected based on degree
Receives a directed graph
"""
import math, networkx as nx
from graph_info import *

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
def contract_score(G):	
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
Returns all the shortest paths
"""
from collections import Counter
def contract_spc(G):
	nx.set_edge_attributes(G, 'shortcut', 0)		# original edges are not shortcuts
	C = []											# list of nodes in the cover
	n = G.number_of_nodes()
	H = nx.nodes(G)									# list of nodes not included in C	
	P = {}											# P[v] is a dict of parents in three rooted at v
	L = {}											# nodes at each level
	Ch = {}											# Ch[v] is a dict of children in the three
	Paths = {}										# Paths[v] dict of paths in the tree
	for v in H:										# compute all shortest paths
		P[v],Paths[v],Ch[v],L[v] = dijkstra_levels(G,v,0)
	
	i = n		
	last = None										# last node added to C									
	while i >=2:									# compute rankings
		total_hits = Counter(dict.fromkeys(H,0))
		for v in H:									# process paths starting at v
			# remove children of last node added to C
			if last in P[v]:						
				p_last = P[v][last]
				Ch[v][p_last].remove(last)			# delete last node from its parent's list of children
				remove_children_of(last,Ch[v],P[v])

			# count the hits and remove descendants of last
			h = Counter(dict.fromkeys(H,0))			# hits of each node in this tree
			l = len(L[v]) - 1						
			while l>=0:								# traverse tree bottom-up
				j = 0
				while j<len(L[v][l]):				# nodes in level l
					u = L[v][l][j]
					if u not in P[v]:
						L[v][l].remove(u)			# u is descendant of last, remove it
						continue
					pu = P[v][u]					# parent of u		
					h[u] = h[u] + 1					# count the (v,u)-path
					h[pu] = h[pu] + h[u]
					j = j+1
				l = l-1
			total_hits = total_hits+h
		
		v = total_hits.most_common(1)[0][0]
		G.node[v]['rank'] = i			
		i = i-1
		last = v		
		H.remove(v)
		C.append(v)	
	#When the loop ends there is just one node remaining in H
	v = H[0]
	G.node[v]['rank'] = 1
	C.append(v)

	#Now we contract in the reverse order of C
	i = n-1
	H = G.copy()
	while i >=1:									# node C[0] is not contracted
		v = C[i] 									# v is to be contracted
		new_edges = shortcut(H,v,Paths)
		for (u,w) in new_edges:				
			H.add_edge(u,w)
			G.add_edge(u,w)
			G[u][w]['shortcut'] = 1
			G[u][w]['dist'] = H[u][w]['dist'] = H[u][v]['dist']+H[v][w]['dist']
		H.remove_node(v)	
		i = i-1
	
	return Paths
	
"""
Shortcuts node v and returns edges that must be added to the graph
Receives the dictionary of paths
"""
def shortcut(H,v,Paths):
	sucs = neighbours(H,v,0)						# successors of v
	if not sucs:
		return []
	new_edges = []	
	pred = neighbours(H,v,1)						# predecessors of v
	for u in pred:
		for w in sucs:
			if u == w or w not in Paths[u] or v not in Paths[u][w]:
				continue	
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

def ch_search(G, source, reverse, target=None, cutoff=None):
	if source == target:
		return ({source: 0}, {source: [source]})
	push = heappush
	pop = heappop
	D = {}  								# dictionary of final distances
	paths = {source: [source]}  			# dictionary of paths
	seen = {source: 0}
	c = count()
	fringe = []  							# use heapq with (distance,label) tuples
	push(fringe, (0, next(c), source))
	while fringe:
		(d, _, v) = pop(fringe)				# min distance and node
		if v in D:
			continue  						# already searched this node.
		D[v] = d							# settle distance
		if v == target:
			break
		N = neighbours(G,v,reverse)
		for w in N:
			if G.node[w]['rank']<G.node[v]['rank']:
				continue	
			vw_dist = D[v] + dist(G,v,w,reverse)
			if cutoff is not None and vw_dist > cutoff:
				continue
			if w not in seen or vw_dist < seen[w]:
				seen[w] = vw_dist
				push(fringe, (vw_dist, next(c), w))
				paths[w] = paths[v] + [w]
	return (D, paths)

"""
Runs a length query from s to t using Contraction Hierarchies
"""
def ch_query(G,s,t):
	Df,_ = ch_search(G,s,0)		#forward search from s
	Db,_ = ch_search(G,t,1)		#backward search from t
	dist = float("inf")
	for u in Df.keys():
		if u in Db and Df[u]+Db[u]<dist:
			dist = Df[u]+Db[u]
	return dist

"""
Runs Dijkstra from the source
Returns list of parents, paths, children and the level of each node (#hops away from source)
"""
def dijkstra_levels(G, source, reverse):
	push = heappush
	pop = heappop
	D = {}  								# dictionary of final distances
	p = {source: source} 	 				# dictionary of parents
	seen = {source: 0}
	h = {source: 0}							# v is h[v] hops away from the source
	levels = {}								# nodes at each level 0,1,2,...
	paths = {source: [source]}  
	c = count()
	fringe = []  							# use heapq with (distance,label) tuples
	push(fringe, (0, next(c), source))
	while fringe:
		(d, _, v) = pop(fringe)				# min distance and node
		if v in D:
			continue  						# already searched this node.
		D[v] = d
		
		hv = h[v]							# settle the level of v
		if hv in levels:
			levels[hv].append(v)
		else:
			levels[hv] = [v] 		

		N = neighbours(G,v,reverse)
		for w in N:	
			vw_dist = D[v] + dist(G,v,w,reverse)
			if w not in seen or vw_dist < seen[w]:
				seen[w] = vw_dist
				push(fringe, (vw_dist, next(c), w))
				p[w] = v
				h[w] = hv + 1
				paths[w] = paths[v] + [w]
	child = {}
	l = 1
	while l<len(levels):					# traverse tree top-bottom to determine children
		for u in levels[l]:
			pu = p[u]
			if pu in child:					# if the node already has children
				child[pu].append(u)
			else:
				child[pu] = [u]
		l = l+1
	return (p,paths,child,levels)

"""
Remove all children of u in the tree
"""
def remove_children_of(u,Ch,P):
	if u in P:
		P.pop(u,None)
	if 	u not in Ch:			# u has no children
		return

	for v in Ch[u]:
		remove_children_of(v,Ch,P)
	Ch.pop(u,None)
