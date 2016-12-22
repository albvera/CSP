#!/usr/bin/python
import networkx as nx
import time
from hub_labels import *; from costs import *; from graph_info import *
from plots import *; from ch import *; from delauney import *
from random import choice

if __name__ == '__main__':
	"""
	G2 = nx.read_gpickle("Data100")
	n = nx.number_of_nodes(G2)
	random.seed(datetime.now())
	m = 30
	B = 2
	sources = list(itertools.product(range(0,n),range(0,B+1)))	#nodes with budget >=0 
	targets = [(u,-1) for u in range(0,n)]						#sink nodes
	randcost(G2,m)
	G = augment(G2,B)
	"""
	G = nx.read_gpickle("DataDirected100")
	start_time = time.time()

	Paths = contract_spc(G)
	tt = time.time() - start_time
	print 'Contraction time: {} secs'.format(tt)
	start_time = time.time()
	
	I,D,N = create_labels(G,Paths)
	tt = time.time() - start_time
	print 'Label construction time: {} secs'.format(tt)
	
	pairs = []
	for k in xrange(0,50):	#Generate random source-destinations pairs
		pairs.append((choice(G.nodes()),choice(G.nodes())))

	for (u,v) in pairs:
		print '({},{}) -- HL:{} -- CH:{} -- SP:{}'.format(u,v,hl_query(I[0][u],D[0][u],I[1][v],D[1][v])-SPlength(G,u,v,0), ch_query(G,u,v)-SPlength(G,u,v,0),SPlength(G,u,v,0))

	#plotlist(N[0].values())
