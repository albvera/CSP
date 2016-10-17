#!/usr/bin/python
import networkx as nx
import time
from hublabels import *; from costs import *; from graphinfo import *
from plots import *; from CH import *; from delauney import *

if __name__ == '__main__':
	G2 = nx.read_gpickle("Data100")
	n = nx.number_of_nodes(G2)
	m = 30
	B = 6
	sources = list(itertools.product(range(0,n),range(0,B+1)))	#nodes with budget >=0 
	targets = [(u,-1) for u in range(0,n)]						#sink nodes
	while m<= 300:	
		random.seed(datetime.now())
		randcost(G2,m)
		start_time = time.time()
		G = augment(G2,B)
		contractSPC(G)
		I,D,N = createlabels(G,sources=sources,targets=targets)
	
		#I,D,N = read_labels("Labels_n100_B6_c70")
		time_pre = 	time.time() - start_time
		"""
		pairs = []
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
		"""
		line = '{}-{}-{}-{}-{}-{}-{}'.format(B,m,time_pre/60,max(N[0].values()),sum(N[0].values())/len(N[0].values()),max(N[1].values()),sum(N[1].values())/len(N[1].values()))
		with open("Output.txt", "a") as myfile:
			myfile.write(line+"\n")
		m = m+10

	#write_labels(I,D,N,"Labels_n100_B6_c70")
	
	#plotlist(N[0].values())		
				
	#plotcolor(G3,'level',1,2)
