#!/usr/bin/python
import networkx as nx
import time
from hub_labels import *; from costs import *; from graph_info import *
from plots import *; from ch import *; from delauney import *
from random import choice
from numpy import average, std

if __name__ == '__main__':
	G= nx.read_gpickle("SF_costs_var")
	random.seed(datetime.now())
	B = 1
	sources = list(itertools.product(G.nodes(),range(0,B+1)))	#nodes with budget >=0 
	targets = [(u,0) for u in G.nodes()]						#sink nodes
	
	with open("SF_data_C", "rb") as f:
		dic = pickle.load(f)
	C = dic['C']
	print 'Instance B={}'.format(B)
	init_time=time.time()
	
	GB = augment(G,B)	
	G_prunned = prune_augmented(G,B)
	print 'Number of edges: G_augmented = {}, G_prunned = {}'.format(nx.number_of_edges(GB),nx.number_of_edges(G_prunned))

	"""
	C = contract_spc(G,rank=True)
	tt = time.time() - start_time
	"""
	
	contract_augmented(G_prunned,C,B)
	print 'Number of shortcuts: {}'.format(sum(nx.get_edge_attributes(G_prunned,'shortcut').values()))

	Id_map = {k: v for v, k in nx.get_node_attributes(G_prunned,'ID').iteritems()}
	I,D,N = create_labels(G_prunned,Id_map,sources=sources,targets=targets)
	
	print '--- Results without prunning ---'
	print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),average(N[0].values()),std(N[0].values()))
	print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),average(N[1].values()),std(N[1].values()))
	
	prune_labels_bootstrap(I,D,N,Id_map,G_prunned)
	print 'Total time: {} secs'.format(time.time() - init_time)
	print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),average(N[0].values()),std(N[0].values()))
	print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),average(N[1].values()),std(N[1].values()))
	
	test_nodes = []									#random (s,t,b) triplets
	for k in xrange(0,1000):		
		test_nodes.append((choice(G.nodes()),choice(G.nodes()),choice(range(0,B+1))))

	init_time = time.time()
	dij_dist = []	
	for k in xrange(0,1000):
		(s,t,b) = test_nodes[k]		
		dij_dist.append(sp_length(GB,(s,b),(t,-1),0))
	dij_time = time.time() - init_time
	
	init_time = time.time()
	hl_dist = []	
	for k in xrange(0,1000):
		(s,t,b) = test_nodes[k]		
		hl_dist.append(hl_query_prunned(I,D,s,t,b))
	hl_time = time.time() - init_time
			
	for k in xrange(0,1000):
		if abs(dij_dist[k]-hl_dist[k]) < 1 or dij_dist[k]==hl_dist[k]:		#Only print if an incorrect result happened
			continue
		print 'Error: (s,t,b)={} -- HL:{} -- Dij:{}'.format(test_nodes[k],hl_dist[k],dij_dist[k])
	print 'Dijkstra query: {} ms, HL query: {} ms'.format(dij_time,hl_time)
