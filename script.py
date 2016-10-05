#!/usr/bin/python
import networkx as nx
import time
from hublabels import *; from costs import *; from graphinfo import *
from plots import *; from CH import *; from delauney import *

if __name__ == '__main__':
	G2 = nx.read_gpickle("DataHierar100")
	n = nx.number_of_nodes(G2)
		
	start_time = time.time()
	"""
	G = G2.to_directed()
	contractSPC(G)
	I,D,N = createlabels(G)
	"""
	
	randcost(G2,70)
	B = 6
	G = augment(G2,B)
	contractSPC(G)
	sources = list(itertools.product(range(0,n),range(0,B+1)))	#nodes with budget >=0 
	targets = [(u,-1) for u in range(0,n)]						#sink nodes
	I,D,N = createlabels(G,sources=sources,targets=targets)
	
	#I,D,N = read_labels("Labels_n100_B5_c30")
	time_pre = 	time.time() - start_time
	
	pairs = []
	random.seed(datetime.now())
	for k in xrange(0,1000):	#Generate random source-destinations pairs
		pairs.append(((random.randint(0,n-1),random.randint(0,B)),(random.randint(0,n-1),-1)))		#for augmented graph
		#pairs.append((random.randint(0,n-1),random.randint(0,n-1)))								#for non-augmented graph

	#print "Hub label queries:"
	start_time = time.time()
	for (u,v) in pairs:
		#print HLquery(I[0][u],D[0][u],I[1][v],D[1][v]) - SPlength(G,u,v,0)
		HLquery(I[0][u],D[0][u],I[1][v],D[1][v])
	time_hl = time.time() - start_time
	
	#print "CH queries:"
	start_time = time.time()	
	for (u,v) in pairs:
		#print CHquery(G,u,v) - SPlength(G,u,v,0)
		SPlength(G,u,v,0)
	
	time_dij = time.time() - start_time
	
	print 'Preprocessing time: {} [s]'.format(time_pre)
	print 'Max forward hub size: {}'.format(max(N[0].values()))
	print 'Average forward hub size: {}'.format(sum(N[0].values())/len(N[0].values()))
	print 'Max backard hub size: {}'.format(max(N[1].values()))
	print 'Average backward hub size: {}'.format(sum(N[1].values())/len(N[1].values()))
	print 'HL query time: {} [ms]'.format(time_hl)
	print 'Dijkstra query time: {} [ms]'.format(time_dij)

	write_labels(I,D,N,"Labels_n100_B6_c70")
	
	#plotlist(N[0].values())		
				
	#plotcolor(G3,'level',1,2)
