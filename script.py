#!/usr/bin/python
import networkx as nx
import time
from hub_labels import *; from costs import *; from graph_info import *
from plots import *; from ch import *; from delauney import *
from random import choice
from numpy import average, std

if __name__ == '__main__':
	name = "SF_costs_var_80_and_90"
	G= nx.read_gpickle(name)
	random.seed(datetime.now())
	B = 20
	sources = list(itertools.product(G.nodes(),range(0,B+1)))	#nodes with budget >=0 
	targets = [(u,0) for u in G.nodes()]						#sink nodes
	
	with open("SF_data_C", "rb") as f:
		dic = pickle.load(f)
	C = dic['C']
	print 'Instance {} with extra edges, B={}'.format(name,B)
	init_time=time.time()
	
	GB = augment(G,B)	
	G_pruned = prune_augmented(G,B)
	print 'Number of edges: G_augmented = {}, G_pruned = {}'.format(nx.number_of_edges(GB),nx.number_of_edges(G_pruned))
	
	#Add edges (v,b)->(v,b-1), hl_query changed
	for v in G.nodes():
		for b in xrange (B,0,-1):
			G_pruned.add_edge((v,b),(v,b-1),dist=0)
	
	"""
	C = contract_spc(G,rank=True)
	tt = time.time() - start_time
	"""
	
	contract_augmented(G_pruned,C,B)
	print 'Number of shortcuts: {}'.format(sum(nx.get_edge_attributes(G_pruned,'shortcut').values()))

	Id_map = {k: v for v, k in nx.get_node_attributes(G_pruned,'ID').iteritems()}
	I,D,N = create_labels(G_pruned,Id_map,sources=sources,targets=targets)
	
	print '--- Results without prunning ---'
	print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),average(N[0].values()),std(N[0].values()))
	print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),average(N[1].values()),std(N[1].values()))
	
	prune_labels_bootstrap(I,D,N,Id_map,G_pruned)
	print 'Total time: {} mins'.format((time.time() - init_time)/60)
	print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),average(N[0].values()),std(N[0].values()))
	print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),average(N[1].values()),std(N[1].values()))
	
	test_nodes = []									#random (s,t,b) triplets
	dij_dist = []	
	hl_dist = []	
	for k in xrange(0,1000):		
		test_nodes.append((choice(G.nodes()),choice(G.nodes()),choice(range(0,B+1))))

	init_time = time.time()
	for k in xrange(0,1000):
		dij_dist.append(sp_length(GB,(test_nodes[k][0],test_nodes[k][2]),(test_nodes[k][1],-1),0))
	dij_time = time.time() - init_time
	
	init_time = time.time()
	for k in xrange(0,1000):		
		hl_dist.append(hl_query_pruned(I,D,test_nodes[k][0],test_nodes[k][1],test_nodes[k][2]))
	hl_time = time.time() - init_time
			
	for k in xrange(0,1000):
		if abs(dij_dist[k]-hl_dist[k]) < 1 or dij_dist[k]==hl_dist[k]:		#Only print if an incorrect result happened
			continue
		print 'Error: (s,t,b)={} -- HL:{} -- Dij:{}'.format(test_nodes[k],hl_dist[k],dij_dist[k])
	print 'Dijkstra query: {} ms, HL query: {} ms'.format(dij_time,hl_time)
