###############################################
#                                             #
# Dependency Index Calculation Module         #
#                                             #
# Module for condensing DSM to                #
# indices using graph theory                  #
# Contrib: uChouinard                         #
# V0 03/03/2019                               #
#                                             #
###############################################

import numpy as np
import networkx as nx
import itertools as iters
import genFN as fzn

def randicIndex(g, alpha=-1./2., _isWeightedCalc=True):
    res=0.
    #res=np.zeros(4);
    weights=nx.get_edge_attributes(g,'weight')
    
    for pair in weights.keys():
            
            if _isWeightedCalc:
                if nx.is_directed(g):
                    res+=  (weights[pair])*np.power( ( g.out_degree(pair[0])*g.in_degree(pair[1]) ) ,alpha)
                else:
                    res+=  (weights[pair])*np.power( ( g.degree(pair[0])*g.degree(pair[1]) ) ,alpha)
            else:
                if nx.is_directed(g):
                    res+=  (1)*np.power( ( g.out_degree(pair[0])*g.in_degree(pair[1]) ) ,alpha)
                else:
                    res+=  (1)*np.power( ( g.degree(pair[0])*g.degree(pair[1]) ) ,alpha)
    return res


def scIndex(g, alpha=-1./2., _isWeightedCalc=True):
    res=0.
    #res=np.zeros(4);
    weights=nx.get_edge_attributes(g,'weight')
    
    for pair in weights.keys():
            
            if _isWeightedCalc:
                if nx.is_directed(g):
                    res+=  (weights[pair])*np.power( ( g.out_degree(pair[0])+g.in_degree(pair[1]) ) ,alpha)
                else:
                    res+=  (weights[pair])*np.power( ( g.degree(pair[0])+g.degree(pair[1]) ) ,alpha)
            else:
                if nx.is_directed(g):
                    res+=  (1)*np.power( ( g.out_degree(pair[0])+g.in_degree(pair[1]) ) ,alpha)
                else:
                    res+=  (1)*np.power( ( g.degree(pair[0])+g.degree(pair[1]) ) ,alpha)
    return res

def wienerIndex(g):
    
    resPath=0
    nodes=nx.nodes(g)
    
    if nx.is_directed(g):
        pairs=iters.permutations(nodes,2)
    else:
        pairs=iters.combinations(nodes,2)
    
    for i in pairs:
        try:
            resPath+=nx.dijkstra_path_length(g,source=i[0],target=i[1] )
        except nx.NetworkXNoPath:
                #print "exception handled"
            resPath+=0
    #print nx.all_pairs_dijkstra_path_length(diG)
    return resPath

def algebraicConnectivity(g):
    
    if nx.is_directed(g):
    
        laplacian=nx.directed_laplacian_matrix(g, weight=None)
    else:
        tmplaplacian=nx.laplacian_matrix(g)
        laplacian=tmplaplacian.todense()
    #print laplacian
    laplacian_eig=np.linalg.eig(laplacian)
    eigs=laplacian_eig[0]
    return np.min(eigs[eigs> 1e-7 ])

def energyIndex(g):
    
    res= np.linalg.eig(nx.to_numpy_matrix(g))
    eigs=res[0]
    
    retValue=0
    if nx.is_directed(g):
        retValue=np.sum(np.abs(np.real(eigs)))
    else:
        retValue=np.sum(np.abs(eigs))    
        
    return retValue

def ChoquetIntegral(measures, scores):
    
    #measure is a Dict containing all fuzzy measures for elements of 
    
    sortedScores=sorted(scores, key=scores.__getitem__)
    
    sortedScoresNames=sorted(scores.keys())
    
    setName=''
    for i in sortedScoresNames:
        setName+=i

    myRes=0
    prevScore=0
    
    for i in sortedScores:
        
        myRes+= (scores[i]-prevScore)*measures[setName]
        
        setName=setName.replace(i,'')
        
        prevScore=scores[i]
        
    return myRes

def dfzn(fzn):
    val = 1.0/3.0 * ( np.sum (fzn ) -( ( fzn[2]*fzn[3] - fzn[0]*fzn[1])
                                               / ((fzn[2]+fzn[3]) - (fzn[0]+fzn[1]) ) ))
    return val

def sigmoid(x,xmin,xmax, L=1., k=1.):
    x0=(xmax+xmin)/2
    res= L/(1+np.exp(-k*(x-x0 )))
    
    
    return res


# A Method to calculate the integration effort based on the ratio of positive
# and negative dependencies of a system
def calc2DIndex(a,b):
    
    return np.sqrt(a**2+b**2)*((1+(b/a)))
    
#calculation of the Negative Dependency Index
#input a DSM object, A dictionary of fuzzy measures, type of index to compute total level of dependencies, normalization method
def calcNDI(dsm, measures, nComponents,indexType='randic',  normType='linear'):
    dicDSM=dsm.getDSM()
    res=0.
    if isinstance(dicDSM, dict):
        scores={}
        for keys in dicDSM:
            
            
            
            if dsm.dsmType is 'interactions':
                minG=nx.DiGraph(2*(-1.+np.identity(nComponents)))
                maxG=nx.DiGraph(2*(1.-np.identity(nComponents)))
            else:
                minG=nx.DiGraph(1*(-1.+np.identity(nComponents)))
                maxG=nx.DiGraph(1*(1.-np.identity(nComponents)))
                
            if indexType is 'randic':
                s=randicIndex(dicDSM[keys])
                smin=randicIndex(minG)
                smax=randicIndex(maxG)
            elif indexType is 'SC':
                s=scIndex(dicDSM[keys])
                smin=scIndex(minG)
                smax=scIndex(maxG)
            elif indexType is 'energy':
                s=energyIndex(dicDSM[keys])
                smin=energyIndex(minG)
                smax=energyIndex(maxG)
            elif indexType is 'algebraic':
                s=algebraicConnectivity(dicDSM[keys])
                smin=algebraicConnectivity(minG)
                smax=algebraicConnectivity(maxG)
            
            if isinstance(s,fzn.genFN):
                s=s.defuz()
            if normType is 'linear':
                scores[keys]=(s-0)/(smax-0)
            elif normType is  'sigmoid':
                scores[keys]=sigmoid(s,smin,smax, 1., 1./2.)
            elif normType is 'none':
                scores[keys]=s
            
			
        res=ChoquetIntegral(measures, scores)
    
    else:
        res=randicIndex(dicDSM)
    #res=float("{0:.3f}".format(res))
    return res