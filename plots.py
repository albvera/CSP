#Assumes that nodes have an attribute 'XY' which are coordinates	
import matplotlib.pyplot as plt, networkx as nx 

#Simple plot
def plot(G):
	#Create dictionary of positions
	points = []
	for n in xrange(G.number_of_nodes()):
		points.append(G.node[n]['XY'])
	pos = dict(zip(range(len(points)), points)) 
	nx.draw(G, pos) 
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
