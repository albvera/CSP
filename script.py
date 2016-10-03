#!/usr/bin/python
import networkx as nx
import time
from hublabels import *
from costs import *
from graphinfo import *
from plots import *

if __name__ == '__main__':
	G2 = nx.read_gpickle("Data100")
	G = G2.to_directed()
	pairs = [(0,7),(4,20),(5,30),(70,90),(14,37),(55,31),(97,48),(77,49),(3,66),(27,33)]
	start_time = time.time()
	
	contractscore(G)
	I,D,N = createlabels(G)
	
	"""
	print "Hub label queries:"
	for (u,v) in pairs:
		print lengthquery(I[0][u],D[0][u],I[1][v],D[1][v]) - SPlength(G2,u,v,0)
	
	print "CH queries:"
	for (u,v) in pairs:
		print CHquery(G,u,v) - SPlength(G2,u,v,0)
	"""
	

	"""
	randcost(G,30)
	Gaug = augment(G,5)
	

	contract(Gaug)
	I,D,N = createlabels(Gaug)
	"""
	
	print 'Elapsed time: {}'.format(time.time() - start_time)

	print sum(N[0].values())
	plotlist(N[0].values())		
