#!/usr/bin/python
import networkx as nx
import time
from hublabels import *; from costs import *; from graphinfo import *
from plots import *; from CH import *; from delauney import *

if __name__ == '__main__':
	G2 = nx.read_gpickle("Data100")
	"""
	#--------- Begin adding extra edges to G2 -----------------
	nx.set_edge_attributes(G2, 'new', 0)
	v1 = closest(G2,0.14,0.8)
	v2 = closest(G2,0.5,0.14)
	v3 = closest(G2,0.75,0.76)
	new_nodes = [v1,v2,v3]
	for u in new_nodes:
		for v in new_nodes:
			if u!=v:
				x1, y1 = G2.node[u]['XY']
				x2, y2 = G2.node[v]['XY']
				dist = math.sqrt( pow( (x2 - x1), 2 ) + pow( (y2 - y1), 2 ) )/4
				G2.add_edge(u,v)
				G2.edge[u][v]['dist'] = round(dist,2)
				G2.edge[u][v]['new'] = 1
	#--------- End adding extra edges to G2 -----------------	
	"""	
		
	start_time = time.time()
	"""
	G = G2.to_directed()
	contractSPC(G)
	I,D,N = createlabels(G)
	"""

	
	randcost(G2,30)
	G = augment(G2,5)
	
	contractSPC(G)
	sources = [(u,B) for u in G.nodes()]
	targets = [(u,-1) for u in G.nodes()]
	I,D,N = createlabels(G)
	
	
	#pairs = [(0,7),(4,20),(5,30),(70,90),(14,37),(55,31),(97,48),(77,49),(19,66),(27,33)]	
	pairs = [((5,0),(4,-1)),((9,2),(19,-1)),((77,5),(32,-1)),((59,3),(8,-1)),((73,0),(57,-1)),((90,2),(11,-1))]	#for augmented graph
	print "Hub label queries:"
	for (u,v) in pairs:
		print HLquery(I[0][u],D[0][u],I[1][v],D[1][v]) - SPlength(G,u,v,0)
	
	print "CH queries:"
	for (u,v) in pairs:
		print CHquery(G,u,v) - SPlength(G,u,v,0)
	
	
	print 'Elapsed time: {}'.format(time.time() - start_time)
	
	plotlist(N[0].values())		
	
	#plotcolor(G3,'level',1,2)
