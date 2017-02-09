import matplotlib.pyplot as plt, networkx as nx, math 
"""
Simple plot when attribute '
Assumes that nodes have coordinates as an attribute 'XY'	
"""
def plot(G):
	pos = nx.get_node_attributes(G,'XY')	#get dictionary of positions
	nx.draw(G, pos, node_size=0.3) 
	plt.show() 

""""
Colors edges depending on an attribute
Attribute takes values: value1, value2, value3(optional)
The colors are: green, blue, red
Example: plot_edge_attributes(G,'shortcut',0,1). If shortcut=0, the edge is plotted green
"""
def plot_edge_attributes(G,attribute,value1,value2,value3=None):
	#Create dictionary of positions
	points = []
	colors = []
	widths = []
	for (u,v) in G.edges():
		if G[u][v][attribute] == value1:
			colors.append('g')
			widths.append(3)
		elif G[u][v][attribute] == value2:
			colors.append('b')
			widths.append(1)
		elif G[u][v][attribute] == value3:
			colors.append('r')
		else:
			colors.append('k')
	for n in xrange(G.number_of_nodes()):
		points.append(G.node[n]['XY'])
	pos = dict(zip(range(len(points)), points)) 
	nx.draw(G, pos,edges=G.edges(),edge_color=colors,width=widths) 
	plt.show() 

""""
sizes is a dictionary indexed by node
Plots grapgh with given width for every node
"""
import matplotlib as mpl
def plot_node_attributes(G,sizes):
	colors = []
	for u in G.nodes():
		colors.append(sizes[u])
	cmap=plt.cm.Reds
	vmin = min(colors)
	vmax = max(colors)
	pos = nx.get_node_attributes(G,'XY')
	nx.draw(G, pos,node_size=10,node_color=colors,cmap=cmap,vmin=vmin,vmax=vmax,with_labels=False,linewidths=0.5) 
	sm = plt.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(vmin=vmin, vmax=vmax))
	sm._A = []
	plt.colorbar(sm)
	plt.show()

#Plot histogram of list or dictionary
import numpy as np
def plot_hist(data,n_bins=30,title="",xlabel="",ylabel=""):
	if isinstance(data,dict):
		data = data.values()
	plt.hist(data,n_bins,alpha=0.5)
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.show()
