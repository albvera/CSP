#!/usr/bin/python
import networkx as nx
import time
from hub_labels import *; from costs import *; from graph_info import *
from plots import *; from ch import *; from delauney import *
from random import choice

if __name__ == '__main__':
	G2 = nx.read_gpickle("DataSF")
	random.seed(datetime.now())
	m = 1000
	B = 2
	sources = list(itertools.product(G2.nodes(),range(0,B+1)))	#nodes with budget >=0 
	targets = [(u,-1) for u in G2.nodes()]						#sink nodes
	randcost(G2,m)
	G = augment(G2,B)
	
	#G = nx.read_gpickle("DataSF")
	start_time = time.time()
	C = contract_spc(G2,rank=True)
	tt = time.time() - start_time
	print 'Cover computation: {} secs'.format(tt)
	start_time = time.time()
	contract_augmented(G,C,B)
	tt = time.time() - start_time
	print 'Contraction: {} secs'.format(tt)

	start_time = time.time()
	Id_map = {k: v for v, k in nx.get_node_attributes(G,'ID').iteritems()}
	I,D,N = create_labels(G,Id_map,sources=sources,targets=targets)
	tt = time.time() - start_time
	print 'Label construction: {} secs'.format(tt)

	start_time = time.time()
	prune_labels(I,D,N,Id_map)
	tt = time.time() - start_time
	print 'Label prunning: {} secs'.format(tt)

	write_labels(I,D,N,"SF_B2_bincreasing")
	
	pairs = []
	for k in xrange(0,50):	#Generate random source-destinations pairs
		pairs.append((choice(sources),choice(targets)))

	for (u,v) in pairs:
		print '({},{}) -- HL:{} -- CH:{} -- SP:{}'.format(u,v,hl_query(I[0][u],D[0][u],I[1][v],D[1][v])-SPlength(G,u,v,0), ch_query(G,u,v)-SPlength(G,u,v,0),SPlength(G,u,v,0))

	plotlist(N[0].values())
