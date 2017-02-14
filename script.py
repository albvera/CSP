#!/usr/bin/python
import networkx as nx
import time, gc
from hub_labels import *; from costs import *; from graph_info import *
from plots import *; from ch import *; from delauney import *
from random import choice
from numpy import average, std
import os

if __name__ == '__main__':
	name = "SF_costs_var"
	technique = "partial_prune"			#frontier, full_prune, partial_prune
	B = 30
	
	this_dir = os.path.dirname(os.path.realpath('__file__'))
	G_dir = os.path.join(this_dir,'SF_data/{}'.format(name))
	G= nx.read_gpickle(G_dir)
	random.seed(datetime.now())
	if technique == "frontier":
		extra_edges = False
	else:
		extra_edges = True	
	if technique == "full_prune":
		omit_forward = True
	else:
		omit_forward = False

	while B<=30:
		sources = list(itertools.product(G.nodes(),range(0,B+1)))	# nodes (s,b) 
		targets = [(u,0) for u in G.nodes()]						# nodes (t,0)	
		init_time=time.time()
		print '\n -----------Instance {}, B={}, {}-----------'.format(name,B,technique)
		
		GB = augment(G,B,extra_edges=extra_edges)	
		G_pruned = prune_augmented(G,B,extra_edges=extra_edges)
		print 'Number of edges: G_augmented = {}, G_pruned = {}'.format(nx.number_of_edges(GB),nx.number_of_edges(G_pruned))
		
		C_dir = os.path.join(this_dir,'SF_data/SF_data_C')	
		with open(C_dir, "rb") as f:
			dic = pickle.load(f)
		C = dic['C']
		
		contract_augmented(G_pruned,C,B)
		print 'Number of shortcuts: {}'.format(sum(nx.get_edge_attributes(G_pruned,'shortcut').values()))

		Id_map = {k: v for v, k in nx.get_node_attributes(G_pruned,'ID').iteritems()}
		I,D,N = create_labels(G_pruned,Id_map,sources=sources,targets=targets)
	
		print 'Results without prunning:'
		print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),int(average(N[0].values())),int(std(N[0].values())))
		print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),int(average(N[1].values())),int(std(N[1].values())))
	
		if technique == "full_prune":	
			G2 = augment(G,B,extra_edges=False)	
			prune_forward_labels(I,D,N,Id_map,G2,G.nodes(),B)
		prune_labels_bootstrap(I,D,N,Id_map,G_pruned,omit_forward=omit_forward,extra_edges=extra_edges)

		hours, rem = divmod(time.time() - init_time, 3600)
		minutes, _ = divmod(rem, 60)
		print 'Total time: {:0>2}:{:0>2}'.format(int(hours),int(minutes))
		print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),int(average(N[0].values())),int(std(N[0].values())))
		print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),int(average(N[1].values())),int(std(N[1].values())))
	
		test_nodes = []												# random (s,t,b) 
		dij_dist = {}	
		hl_dist = {}	
		for k in xrange(0,1000):		
			test_nodes.append((choice(G.nodes()),choice(G.nodes()),choice(range(0,B+1))))

		query_hl = hl_query_extra_edges
		query_dijkstra = dijkstra_sink
		if technique == "frontier":
			test_nodes = [(s,t,B) for (s,t,b) in test_nodes]	
			query_hl = hl_query_frontier
			query_dijkstra = dijkstra_frontier

		init_time = time.time()
		for k in xrange(0,1000):
			dij_dist[k] = query_dijkstra(GB,test_nodes[k][0],test_nodes[k][1],test_nodes[k][2])
		dij_time = time.time() - init_time
	
		init_time = time.time()
		for k in xrange(0,1000):		
			hl_dist[k] = query_hl(I,D,test_nodes[k][0],test_nodes[k][1],test_nodes[k][2])
		hl_time = time.time() - init_time
	
		for k in xrange(0,1000):
			if dij_dist[k] != hl_dist[k]:
				print 'Error {}: (s,t)={} -- HL:{} -- Dij:{}'.format(k,test_nodes[k],hl_dist[k],dij_dist[k])
		print 'Dijkstra query: {} ms, HL query: {} ms'.format(dij_time,hl_time)	

		write_labels(I,D,N,Id_map,'{}_B{}_labels_{}'.format(name,B,technique))
		B+=5
		I = D = N = G_pruned = None
		gc.collect()
