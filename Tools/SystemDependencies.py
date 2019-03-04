######################################################################################
#                                                                                    #
# System + Dependency creation Module                                                #
# Contrib: uChouinard                         #
# V0 2/12/2016                                #
#                                             #
###############################################

import genFN as fzN
import numpy as np
import DSM as dsmx



def getEA(effectName='Heat'):
        att = {'Heat' : fzN.genFN(np.array( [0.55, 0.70, 0.70, 0.85]),10, 'trap', 'heat'), 
                        'Vibration':fzN.genFN(np.array( [0.15, 0.30, 0.30, 0.45]),10, 'trap', 'vibe'), 
                        'EMF': fzN.genFN(np.array( [0.75,1.,1.,1.]),10, 'trap', 'ef') }
        return att[effectName]
    
class AdverseEffect:
    
    def __init__(self, eType, lvl ):
        
        self.etype=eType
        self.lvl=lvl
    def rtType(self):
        return self.etype
    
    def rtLvl(self):
        return self.lvl
    
class Function:
    
    def __init__(self, fType,lvl ):
        
        self.fType=fType
        self.lvl=lvl
    def rtType(self):
        return self.name
    
    def rtLvl(self):
        return self.lvl
    

class Component:
    
    def __init__(self, name, compType='', subLevels=''):
        
        self.name=name
        self.compType=compType
        self.subLevels=subLevels
        self.fullname=name+compType+subLevels
        self.affecting = []
        self.affected = []
        self.reqF=[]
        self.genF=[]
        self.criteriaList={}
        
    def addAffecting(self, adEff):
        self.affecting.append(adEff)
        
    def addAffected(self, adEff):
        self.affected.append(adEff)
        
    def addFunctionReq(self, adF):
        self.reqF.append(adF)
    
    def addFunctionGen(self, adF):
        self.genF.append(adF)
        
    def addCriteria(self, criteria):
        self.criteriaList.update(criteria)
    
        
    def __repr__(self):
        
        return repr(self.name)
    
class AdverseEffectDependency:
    
    def __init__(self, affecter, affected, dtype, affecting_l, affected_l, closenessF, attenuation_l=''):
        
        
        #print(affecting_l)
        #print(affected_l)
        self.affecter = affecter
        self.affected = affected
        self.dependencyType = dtype
        
        if affecting_l is 'nan' or affecting_l is '':
            self.l_affecting = fzN.getLFV('n')
        else:
            self.l_affecting = fzN.getLFV(affecting_l)
            
        if affected_l is 'nan' or affected_l is '':
            self.l_affected = fzN.getLFV('n')
        else:
            self.l_affected = fzN.getLFV(affected_l)
            
        if closenessF is 'nan' or closenessF is '':
            self.closenessF=fzN.getLFV('n')
        else:
            self.closenessF=fzN.getLFV(closenessF)
        
        if attenuation_l is '' or attenuation_l is 'nan':
            self.attLvl= getEA(dtype)
        else:
            self.attLvl=fzN.getLFV(attenuation_l)
        self.dpval=0
        self.defuzval=0
        
        
    def calcDepVal(self, method='GM'):
        fzOne=fzN.genFN([1,1,1,1],10,'trap')
        if self.closenessF.name is 'n':
            self.dpval=fzN.getLFV('n')
        else:
            if method is 'GM':
                
                #print (max((fzOne-self.attLvl),self.closenessF))
                self.dpval=  fzN.fzGM( [self.l_affecting,self.l_affected, max((fzOne-self.attLvl),self.closenessF)] )
                #self.dpval=  fzN.fzGM( [self.l_affecting,self.l_affected, (fzOne-self.attLvl)*self.closenessF] )
            elif method is 'AM':
                self.dpval= fzN.fzAM( [self.l_affecting,self.l_affected, max((fzOne-self.attLvl),self.closenessF)] )
        #print (fzOne-self.attLvl)
        return self
    
    def toNPArr(self):
        
        self.dpval= self.dpval.toNPArr()
        return self
    
    def depDefuz(self):
        
        x=1.*self.dpval.defuz()
        #self.defuzval=float("{0:.5f}".format(x))
        self.defuzval=x
        return self
    
    def __repr__(self):
        
        return repr([self.affecter, self.affected, self.dependencyType, self.dpval])
    
class FunctionalDependency:
    
    def __init__(self, antecedent , dependent, fType ,l_ant, l_dep):
        
        self.antecedent = antecedent
        self.dependent = dependent
        self.dependencyType = fType
        self.l_ant = fzN.getLFV(l_ant)
        self.l_dep = fzN.getLFV(l_dep)
        
        self.dpval=0
        self.defuzval=0
        
    def calcDepVal(self, method='GM'):
        #if method is 'GM':
        #    self.dpval= fzN.fzGM( [self.l_ant,self.l_dep] )
        #elif method is 'AM':
        #    self.dpval= fzN.fzAM( [self.l_ant,self.l_dep] )
        
        self.dpval=fzN.genFN([1,1,1,1],10,'trap')+(self.l_ant-self.l_dep)
        #print (self.dependencyType)
        #print (self.dpval)
        
        return self
        
    def depDefuz(self):
        
        x=self.dpval.defuz()
        self.defuzval=float("{0:.2f}".format(x))
        return self
        
class System:
    
    def __init__(self, name):
        
        self.buildType=''
        self.name=name;
        
        self.components=[]
        
        self.closeness={}
        
        self.attenuation={'Heat':'', 'Vibration':'', 'EMF':''}
        
        self.adverseDependencies=[]
        
        self.functionalDependencies=[]
        self.funcDepTypes=[]
        
        self.adverseDSM=dsmx.DSM(name+'adversesDep', 'dependencies','yes' )
        self.functionDSM=dsmx.DSM(name+'funcDep', 'functional','yes')
        
        self.totAdvDSM={}
    
    def addComponents(self,cList):
        self.components.extend(cList)
        
        [self.adverseDSM.addComponent([x.fullname]) for x in cList]
        
    def addCloseness(self, cList):
        self.closeness=cList
    
    def findDeps(self):
        deplist=[AdverseEffectDependency(a.fullname,b.fullname,c.etype,c.lvl,d.lvl, 
                                         self.closeness[('/'.join(sorted([a.fullname, b.fullname])))], self.attenuation[c.etype])  
            for a in self.components for b in self.components for c in a.affecting for d in b.affected if c.etype == d.etype ]

        self.adverseDependencies=[x.calcDepVal() for x in deplist]
        #print self.adverseDependencies
        
        deplist2=[FunctionalDependency(a.fullname,b.fullname,c.fType,c.lvl,d.lvl)  
            for a in self.components for b in self.components for c in a.genF for d in b.reqF 
           if set(c.fType) == set(d.fType) ]

        self.functionalDependencies=[x.calcDepVal() for x in deplist2]
    
    def findDSMs(self, nType='fuzzy'):
        
        
        if nType is 'fuzzy':

            #deplist=[y.toNPArr() for y in deplist]
       
            #find all heat relations
            [self.adverseDSM.addRelation([x.affecter], [x.affected],[{ 'h':x.dpval}]) 
             for x in self.adverseDependencies if x.dependencyType=='Heat' ]
    
            #find all vibration relations
            [self.adverseDSM.addRelation([x.affecter], [x.affected],[{ 'v':x.dpval}])
             for x in self.adverseDependencies if x.dependencyType=='Vibration' ]
    
            #find all EMF relations
            [self.adverseDSM.addRelation([x.affecter], [x.affected],[{ 'e':x.dpval}])
             for x in self.adverseDependencies if x.dependencyType=='EMF' ]
            
            #find all information relations
            [self.functionDSM.addRelation([x.antecedent], [x.dependent],[{ 'i':x.dpval}])
             for x in self.functionalDependencies if  'Information' in x.dependencyType  ]
            
            #find all Energy relations
            [self.functionDSM.addRelation([x.antecedent], [x.dependent],[{ 'e':x.dpval}])
             for x in self.functionalDependencies if 'Energy' in x.dependencyType  ]
            
        elif nType is 'float':
            self.adverseDependencies=[y.depDefuz() for y in self.adverseDependencies]
            self.functionalDependencies=[y.depDefuz() for y in self.functionalDependencies]
            #deplist=[y.toNPArr() for y in deplist]
       
    
            [self.adverseDSM.addRelation([x.affecter], [x.affected],[{ 'h':x.defuzval}]) 
             for x in self.adverseDependencies if x.dependencyType=='Heat' ]
    
   
            [self.adverseDSM.addRelation([x.affecter], [x.affected],[{ 'v':x.defuzval}])
             for x in self.adverseDependencies if x.dependencyType=='Vibration' ]
    
    
            [self.adverseDSM.addRelation([x.affecter], [x.affected],[{ 'e':x.defuzval}])
             for x in self.adverseDependencies if x.dependencyType=='EMF' ]
        
            [self.functionDSM.addRelation([x.antecedent], [x.dependent],[{ 'i':x.defuzval}])
             for x in self.functionalDependencies if 'Information' in x.dependencyType  ]
            
            [self.functionDSM.addRelation([x.antecedent], [x.dependent],[{ 'e':x.defuzval}])
             for x in self.functionalDependencies if 'Energy' in x.dependencyType ]
        
        
    def build(self, nType='fuzzy'):
        
        self.buildType=nType
        self.findDeps()
        self.findDSMs(nType)
        
    
    def totDepVal(self,a,b,dType='adverse'):
        #if nType is 'fuzzy':
        #    res=fzN.genFN([0,0,0,0], 10, 'trap')
        #else:
        #    res=0.
        resList={}
        if dType is 'adverse':
            depVals=self.adverseDSM.getRelation(a,b)
            #print (depVals)
            depVals=dict((k,v) for k,v in depVals.items() if v is not None)
            for key in depVals:
                
                resList[key]=depVals[key]['weight']
            #print (resList)
            #print (resList.values())
        elif dType is 'function':
            #self.functionDSM.display()
            depVals=self.functionDSM.getRelation(a,b)
            #print (depVals)
            depVals=dict((k,v) for k,v in depVals.items() if v is not None)
            for key in depVals:
                
                resList[key]=depVals[key]['weight']
                
        if self.buildType is 'fuzzy':        
            if  resList:
                res=fzN.fzGM(list(resList.values()))       
            else:
                if dType is 'adverse':
                    res=fzN.genFN([0,0,0,0], 10, 'trap') 
                else:
                    res=fzN.genFN([1,1,1,1], 10, 'trap') 
        else:
            if  resList:
                res=np.mean(list(resList.values()))       
            else:
                if dType is 'adverse':
                    res=0 
                else:
                    res=1
        return res
            
        
        
    def showDSM(self):
        self.adverseDSM.display()
        self.functionDSM.display()
        
        
        