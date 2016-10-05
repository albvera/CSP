import matplotlib.pyplot as plt, networkx as nx 
"""
Simple plot when attribute '
Assumes that nodes have coordinates as an attribute 'XY'	
"""
def plot(G):
	#Create dictionary of positions
	points = []
	for n in xrange(G.number_of_nodes()):
		points.append(G.node[n]['XY'])
	pos = dict(zip(range(len(points)), points)) 
	nx.draw(G, pos) 
	plt.show() 

""""
Colors edges depending on an attribute
Attribute takes values: value1, value2, value3(optional)
The colors are: green, blue, red
"""
def plotcolor(G,attribute,value1,value2,value3=None):
	#Create dictionary of positions
	points = []
	colors = []
	for (u,v) in G.edges():
		if G[u][v][attribute] == value1:
			colors.append('g')
		elif G[u][v][attribute] == value2:
			colors.append('b')
		elif G[u][v][attribute] == value3:
			colors.append('r')
		else:
			colors.append('k')
	for n in xrange(G.number_of_nodes()):
		points.append(G.node[n]['XY'])
	pos = dict(zip(range(len(points)), points)) 
	nx.draw(G, pos,edges=G.edges(),edge_color=colors) 
	plt.show() 


#Plot with shortcut edges

#Plot histogram of list
from collections import Counter
import numpy as np
def plotlist(l):
	labels, values = zip(*Counter(l).items())

	indexes = np.arange(len(labels))
	width = 1

	plt.bar(indexes, values, width)
	plt.xticks(indexes + width * 0.5, labels)
	plt.show()
