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
