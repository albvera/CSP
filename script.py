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
	
	init_time=start_time=time.time()
	GB = augment(G,B)
	tt = time.time() - start_time
	print 'Augmentation: {} secs'.format(tt)

	start_time = time.time()
	G_prunned = prune_augmented(G,B)
	tt = time.time() - start_time
	print 'Prunning augmented graph: {} secs'.format(tt)
	print 'Number of edges: G_augmented = {}, G_prunned = {}'.format(nx.number_of_edges(GB),nx.number_of_edges(G_prunned))

	"""
	init_time = time.time()
	start_time = time.time()
	C = contract_spc(G,rank=True)
	tt = time.time() - start_time
	print 'Cover computation: {} secs'.format(tt)
	"""

	start_time = time.time()
	contract_augmented(G_prunned,C,B)
	tt = time.time() - start_time
	print 'Contraction: {} secs'.format(tt)
	print 'Number of shortcuts: {}'.format(sum(nx.get_edge_attributes(G_prunned,'shortcut').values()))

	start_time = time.time()
	Id_map = {k: v for v, k in nx.get_node_attributes(G_prunned,'ID').iteritems()}
	I,D,N = create_labels(G_prunned,Id_map,sources=sources,targets=targets)
	tt = time.time() - start_time
	print 'Label construction: {} secs'.format(tt)

	print '--- Results without prunning ---'
	print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),average(N[0].values()),std(N[0].values()))
	print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),average(N[1].values()),std(N[1].values()))
	
	start_time = time.time()
	prune_labels_bootstrap(I,D,N,Id_map,G_prunned)
	tt = time.time() - start_time
	print 'Label prunning: {} secs'.format(tt)
	print 'Total time: {} secs'.format(time.time() - init_time)
	print 'Max F:{}, Avg F:{}, Std F: {}'.format(max(N[0].values()),average(N[0].values()),std(N[0].values()))
	print 'Max B:{}, Avg B:{}, Std B: {}'.format(max(N[1].values()),average(N[1].values()),std(N[1].values()))
	
	for k in xrange(0,1000):		#Generate random source-destinations pairs
		s = choice(G.nodes())
		t = choice(G.nodes())
		b = choice(range(0,B+1))
		hl_dist = hl_query_prunned(I,D,s,t,b)
		dij_dist = sp_length(GB,(s,b),(t,-1),0)
		if abs(dij_dist-hl_dist) < 1 or dij_dist==hl_dist:		#Only print if an incorrect result happened
			continue
		print 'Diff:{} -- (s,t,b)=({},{},{}) -- HL:{} -- Dij:{}'.format(dij_dist-hl_dist,s,t,b,hl_dist,dij_dist)
