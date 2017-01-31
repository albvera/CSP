import math, networkx as nx
from graph_info import *
import time, progressbar

"""
Uses shortest path covers to contract
Adds nodes greedily to a cover C and then contract in reverse order
Returns all the shortest paths
If rank=True, then returns the cover when the rank is computed and skips the contraction
"""
from collections import defaultdict
def contract_spc(G,rank=False):
	nx.set_edge_attributes(G, 'shortcut', 0)		# original edges are not shortcuts
	C = []											# list of nodes in the cover
	n = G.number_of_nodes()
	H = nx.nodes(G)									# list of nodes not included in C	
	P = {}											# P[v] is a dict of parents in three rooted at v
	L = {}											# nodes at each level
	Ch = {}											# Ch[v] is a dict of children in the three
	Paths = {}										# Paths[v] dict of paths in the tree
	print 'Computing paths for cover'
	bar = progressbar.ProgressBar()
	for v in bar(H):										# compute all shortest paths
		P[v],Paths[v],Ch[v],L[v] = dijkstra_levels(G,v,0)
	
	print 'Computing SPC'	
	last = None										# last node added to C			
	bar = progressbar.ProgressBar()						
	for i in bar(xrange(n,1,-1)):						# i = n,n-1,...,2
		total_hits = dict.fromkeys(H,0)
		for v in H:									# process paths starting at v
			# remove children of last node added to C
			if last in P[v]:						
				p_last = P[v][last]
				Ch[v][p_last].remove(last)			# delete last node from its parent's list of children
				remove_children_of(last,Ch[v],P[v])

			# count the hits and remove descendants of last
			h = defaultdict(int)					# hits of each node in this tree
			h[v] = 1					
			for l in xrange(len(L[v])-1,0,-1):		# traverse tree bottom-up
				j = 0
				len_L = len(L[v][l])
				while j<len_L:						# nodes in level l
					u = L[v][l][j]
					if u not in P[v]:
						L[v][l].remove(u)			# u is descendant of last, remove it
						len_L = len_L-1
						continue
					pu = P[v][u]					# parent of u		
					h[u] = h[u] + 1					# count the (v,u)-path
					h[pu] = h[pu] + h[u]
					j = j+1
			for u in h.keys():
				total_hits[u] = total_hits[u]+h[u]
		
		last = max(total_hits, key = total_hits.get)
		G.node[last]['rank'] = i			
		H.remove(last)
		C.append(last)	
	#When the loop ends there is just one node remaining in H
	v = H[0]
	G.node[v]['rank'] = 1
	C.append(v)
	
	if rank:
		return C
	
	#Now we contract in the reverse order of C
	print 'Contracting'
	H = G.copy()
	bar = progressbar.ProgressBar()
	for i in bar(xrange(n-1,0,-1)):					# node C[0] is not contracted
		v = C[i] 									# v is to be contracted
		new_edges = shortcut(H,v,Paths)
		for (u,w) in new_edges:				
			H.add_edge(u,w)
			G.add_edge(u,w)
			G[u][w]['shortcut'] = 1
			G[u][w]['dist'] = H[u][w]['dist'] = H[u][v]['dist']+H[v][w]['dist']
		H.remove_node(v)	
	
"""
Uses a rank specified by a permutation C of the original nodes to contract an augmented graph
"""
def contract_augmented(G,C,B):
	nx.set_edge_attributes(G, 'shortcut', 0)		# original edges are not shortcuts
	nx.set_node_attributes(G, 'rank', 0)			# rank of sink nodes
	nn = len(C)										# number of original nodes
	H = G.copy()
	rank = 1
	dijkstra = nx.single_source_dijkstra
	successors = H.successors
	predecessors = H.predecessors
	remove_node = H.remove_node
	
	bar = progressbar.ProgressBar()
	print 'Contracting augmented graph'
	for i in bar(xrange(nn-1,-1,-1)):
		for b in xrange(B,-1,-1):				
			v = (C[i],b)							# v is to be contracted
			if not G.has_node(v):					# when the augmented graph is pruned some nodes disappear 
				continue
			G.node[v]['rank'] = rank
			rank += 1
			sucs = successors(v)					# successors of v
			if not sucs:							# v has no successors
				remove_node(v)
				continue
			pred = predecessors(v)					# predecessors of v
			if not pred:							# v has no predecessors
				remove_node(v)
				continue
		
			#Look in G for cutoff. If look in H, then better (larger) cutoff but takes longer
			max_vw = 0								# max dist(v,w)
			for w in G[v]:							# search in successors of v
				if G[v][w]['dist'] > max_vw:
					max_vw = G[v][w]['dist']
			
			for u in pred:
				_,Paths = dijkstra(H,u,target=None,cutoff=G[u][v]['dist']+max_vw, weight='dist')
				for w in sucs:
					if u == w or v not in Paths[w]:
						continue	
					H.add_edge(u,w,dist=H[u][v]['dist']+H[v][w]['dist'])
					G.add_edge(u,w,shortcut=1,dist=H[u][v]['dist']+H[v][w]['dist'])
			remove_node(v)
	
"""
Shortcuts node v and returns edges that must be added to the graph
Receives the dictionary of paths
"""
def shortcut(H,v,Paths):
	sucs = H.successors(v)						# successors of v
	if not sucs:
		return []
	new_edges = []	
	pred = H.predecessors(v)					# predecessors of v
	for u in pred:
		for w in sucs:
			if u == w or w not in Paths[u] or v not in Paths[u][w]:
				continue	
			new_edges.append((u,w))
	return new_edges


"""
Runs a CH search, visiting all nodes with higher rank
rank is a dictionary indexed by nodes
The output is a pair (D,P) where D[v] is the distance from start to v and P[v] is the predecessor of v along the shortest path from s to v.
"""
from heapq import heappush, heappop
from itertools import count

def ch_search(G, source, reverse, rank):
	push = heappush
	pop = heappop
	D = {}  								# dictionary of final distances
	parent = {source: source}  				# dictionary of parents
	seen = {source: 0}
	c = count()
	fringe = []  							# use heapq with (distance,label) tuples
	push(fringe, (0, next(c), source))
	if reverse == 0:
		dist = dist_forward
		neighbours = G.successors
	else:
		dist = dist_backward
		neighbours = G.predecessors

	while fringe:
		(d, _, v) = pop(fringe)				# min distance and node
		if v in D:
			continue  						# already searched this node.
		D[v] = d							# settle distance
		N = neighbours(v)
		for w in N:
			if rank[w]<rank[v]:
				continue	
			vw_dist = D[v] + dist(G,v,w)
			if w not in seen or vw_dist < seen[w]:
				seen[w] = vw_dist
				push(fringe, (vw_dist, next(c), w))
				parent[w] = v
	return (D, parent)

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
	#TODO:implement a function here to call dist and neighbours
	if reverse == 0:
		dist = dist_forward
	else:
		dist = dist_backward
	while fringe:
		(d, _, v) = pop(fringe)				# min distance and node
		if v in D:
			continue  						# already searched this node.
		D[v] = d
		hv = h[v]						# settle the level of v
		if hv in levels:
			levels[hv].append(v)
		else:
			levels[hv] = [v] 		

		N = neighbours(G,v,reverse)
		for w in N:	
			vw_dist = D[v] + dist(G,v,w)
			if w not in seen or vw_dist < seen[w]:
				seen[w] = vw_dist
				push(fringe, (vw_dist, next(c), w))
				p[w] = v
				paths[w] = paths[v] + [w]
				h[w] = hv + 1
	
	child = {}
	for l in xrange(1,len(levels)):			# traverse tree top-bottom to determine children
		for u in levels[l]:
			pu = p[u]
			if pu in child:					# if the node already has children
				child[pu].append(u)
			else:
				child[pu] = [u]

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
