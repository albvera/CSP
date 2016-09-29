"""
Creates Delaunay triangulation from a set of (x,y) points
Example: points = [(0,0),(0,1),(2,2),(3,4),(4,3)] 
Returns an undirected graph represented with networkx library
Creates ID attribute
"""
import math, scipy.spatial, networkx as nx

def delauney(points):
	# make a Delaunay triangulation 
	delTri = scipy.spatial.Delaunay(points) 

	# create a set for edges that are indexes of the points 
	edges = set() 
	# for each Delaunay triangle 
	for n in xrange(delTri.nsimplex): 
    	# for each edge of the triangle 
    	# sort the vertices 
    	# (sorting avoids duplicated edges being added to the set) 
    	# and add to the edges set 
		edge = sorted([delTri.vertices[n,0], delTri.vertices[n,1]]) 
		edges.add((edge[0], edge[1])) 
		edge = sorted([delTri.vertices[n,0], delTri.vertices[n,2]]) 
		edges.add((edge[0], edge[1])) 
		edge = sorted([delTri.vertices[n,1], delTri.vertices[n,2]]) 
		edges.add((edge[0], edge[1])) 
	# make a graph based on the Delaunay triangulation edges 
	graph = nx.Graph(list(edges)) 
	#add positions (x,y) as attributes
	for n in xrange(len(points)):
		graph.node[n]['XY'] = points[n]
		graph.node[n]['ID'] = n

	# calculate Euclidian length of edges and write it as edges attribute
	edges = graph.edges()
	for i in xrange(len(edges)):
		edge = edges[i]
		node_1 = edge[0]
		node_2 = edge[1]
		x1, y1 = graph.node[node_1]['XY']
		x2, y2 = graph.node[node_2]['XY']
		dist = math.sqrt( pow( (x2 - x1), 2 ) + pow( (y2 - y1), 2 ) )
		graph.edge[node_1][node_2]['dist'] = round(dist,2)
	
	return graph;

"""
Creates a random graph by sampling n uniform points in [0,1]x[0,1]
Saves in a file named 'name' using pickle, it is easily read by networkx
Example: randomdelauney(20,"example")
"""
import random 
from datetime import datetime

def randomdelauney(n,name):
	#initialize random seed
	random.seed(datetime.now())
	points = []
	for i in range(n):
		points.append((random.random(),random.random()))
	
	# make a Delaunay triangulation 
	G = delauney(points)
	nx.write_gpickle(G,name)
