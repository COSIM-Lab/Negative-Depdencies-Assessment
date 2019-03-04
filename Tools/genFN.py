import numpy as np
import copy
import matplotlib.pyplot as plt

class genFN:
    
    
    def __init__(self, fn, nDiscretized, fnType='trap', name=None):
        
        alphax=np.linspace(0.0,1.0, num=nDiscretized+1)
        self.step=1./(nDiscretized)
        self.alphax=alphax;
        self.fnType=fnType;
        #self.fuzNum=np.zeros(2*alphax.shape)
        self.fuzNum=0.
        self.name=name
        
        if fnType is 'trap':
            L=np.zeros(alphax.shape)
            R=np.zeros(alphax.shape)
            if len(fn) is 4:
                L=fn[0]+alphax*(fn[1]-fn[0])
                R=fn[3]-alphax*(fn[3]-fn[2])
                self.fuzNum= np.append(L,np.flipud(R))
    def __repr__(self):
        return str(self.fuzNum)
    
    def __add__(self, other):
        
        res=copy.copy(self)
        if isinstance(other,genFN):
            res.fuzNum=res.fuzNum+other.fuzNum
        elif isinstance(other, float) or isinstance(other, int):
            res.fuzNum=res.fuzNum+other*np.zeros(self.fuzNum.shape)
        return res
    def __sub__(self,other):
        res=copy.copy(self)
        if isinstance(other,genFN):
            res.fuzNum=res.fuzNum-np.flipud(other.fuzNum)
            
        return res
    def __truediv__(self, other):
        res=copy.copy(self)
        if isinstance(other,genFN):
            tmp=copy.copy(other)
            tmp.fuzNum=np.ones(tmp.fuzNum.shape)/np.flipud(tmp.fuzNum)
            res=res*tmp
        return res
            
    def __radd__(self, other):
        
        res=copy.copy(self)
        if isinstance(other,genFN):
            res.fuzNum=res.fuzNum+other.fuzNum
        elif isinstance(other, float) or isinstance(other, int):
            res.fuzNum=res.fuzNum+other*np.zeros(self.fuzNum.shape)
        return res
    
    def __mul__(self, other):
        
        
        if isinstance(other,genFN):
            res=copy.copy(self)
            matSL=self.fuzNum[0:len(self.alphax)]
            #print matSL
            matOL=other.fuzNum[0:len(other.alphax)]
            matSR=np.flipud(self.fuzNum[len(self.alphax):])
            matOR=np.flipud(other.fuzNum[len(other.alphax):])
        
            resmat=np.array([matSL*matOL,matSL*matOR, matSR*matOL, matSR*matOR])
            #print resmat
        
            lower=np.amin(resmat, axis=0)
            upper=np.amax(resmat,axis=0)
        
            res.fuzNum=np.append(lower, np.flipud(upper))
        elif isinstance(other, float) or isinstance(other, int):
            res=copy.copy(self)
            matSL=self.fuzNum[0:len(self.alphax)]
            matSR=np.flipud(self.fuzNum[len(self.alphax):])
        
            resmat=np.array([matSL*other, matSR*other])
            #print resmat
        
            lower=np.amin(resmat, axis=0)
            upper=np.amax(resmat,axis=0)
        
            res.fuzNum=np.append(lower, np.flipud(upper))
        else:
            print ("in radd genfn none")
            res=None
        return res
    def __rmul__(self,other):
        
        if isinstance(other, float) or isinstance(other, int):
            res=copy.copy(self)
            matSL=self.fuzNum[0:len(self.alphax)]
            matSR=np.flipud(self.fuzNum[len(self.alphax):])
        
            resmat=np.array([matSL*other, matSR*other])
            #print resmat
        
            lower=np.amin(resmat, axis=0)
            upper=np.amax(resmat,axis=0)
        
            res.fuzNum=np.append(lower, np.flipud(upper))
        else:
            print ("in rmul genfn none")
            res=None
        return res
    
    def __eq__(self, other):
        
        return self.value() == other.value() 
        
    def __gt__(self, other):
        
        return self.value() > other.value()
        
    def __lt__(self, other):
        
        return self.value()<other.value()
    
    def __invert__(self):
        res=copy.copy(self)
        
        res.alphax= np.flipud(res.alphax)
        
        return res

    def defuz(self):
        
        a=np.append(self.alphax, np.flipud(self.alphax))
        
        res=np.sum( a*self.fuzNum)/np.sum(a)
        return res
    
    def value(self):
        
        res= np.sum(self.alphax*(self.fuzNum[:len(self.alphax)]+np.flipud(self.fuzNum[len(self.alphax):]))*self.step)
        
        return res
    
    def ambiguity(self):
        res= np.sum(self.alphax*(np.flipud(self.fuzNum[len(self.alphax):])-self.fuzNum[:len(self.alphax)])*self.step)
        
        return res
    
    def fuzziness(self):
        middle = (np.abs(self.alphax-0.5)).argmin()
        L=self.fuzNum[:len(self.alphax)]
        R=np.flipud(self.fuzNum[len(self.alphax):])
        alphax=self.alphax
        alphaxInv=np.flipud(alphax)
        
        #boundsInt=np.sum(self.step*alphax*(R[0]-L[0]))
        #lowUpInv=np.sum(self.step*alphaxInv[middle:]*(L[0:middle+1]-L[0]))
        #coreUp=np.sum(self.step*alphax[middle:]*(R[middle:]-L[middle:]) )
        #upUpInv=np.sum(self.step*alphaxInv[middle:]*(R[0]-R[0:middle+1]))
        #lowLow=np.sum(self.step*alphax[:middle]*(L[:middle]-L[0]) )
        #coreLowInv=np.sum(self.step*alphaxInv[:middle]*(R[:middle] -L[:middle]) )
        #upLow=np.sum( self.step*alphax[:middle]*(R[0]-R[0:middle] ))
        
        #res=boundsInt-(lowUpInv+coreUp+upUpInv+lowLow+coreLowInv+upLow)
        
        low=np.sum(self.step*(R[:middle]-L[:middle]))
        up=np.sum(self.step*(L[middle:]-R[middle:]))
        res=low+up
        return res
    
def plotFZN(fn):
    
    plt.figure()
    plt.plot(fn.fuzNum, np.append(fn.alphax, np.flipud(fn.alphax)))
    plt.show()
    
    
def fzAM(fznList):
        
        if fznList:
            res = copy.copy(fznList[0])

            for i in range(1,len(fznList)):
                res +=  fznList[i]
            res.fuzNum=res.fuzNum/len(fznList)
        else:
            res=genFN([0,0,0,0], 10, 'trap')

        return res

def fzGM(fznList):
        #print fznList
        
        if fznList:
            res = copy.copy(fznList[0])

            for i in range(1,len(fznList)):
                res =res * fznList[i]
            res.fuzNum=np.power(res.fuzNum,1.0/len(fznList))
        else:
            res=genFN([0,0,0,0], 10, 'trap')
        return res
    
def fzHM(fznList):
        
        
        if fznList:
            res = copy.copy(fznList[0])
            fzOne=copy.copy(fznList[0])
            fzOne.fuzNum=np.ones(fzOne.fuzNum.shape)
            
            for i in range(1,len(fznList)):
                res =res + fzOne/fznList[i]
            res.fuzNum=res.fuzNum/len(fznList)
            res=fzOne/res
        else:
            res=genFN([0,0,0,0], 10, 'trap')
        return res
    
def getLFV(lfvName = 'm', lfvType='trap'):

        arr=0.0
        if lfvName =='n':
            arr=np.array([ 0.00, 0.00, 0.00, 0.])
        elif lfvName =='vl' or lfvName =='vb':
            arr=np.array([ 0.00, 0.00, 0.00, 0.25])
        elif lfvName== 'l'or lfvName =='b':
            arr=np.array([0.15, 0.30, 0.30, 0.45])
        elif lfvName=='m' or lfvName =='a':
            arr=np.array([ 0.35, 0.50, 0.50, 0.65])
        elif lfvName== 'h' or lfvName =='g':
            arr=np.array([0.55, 0.70, 0.70, 0.85])
        elif lfvName== 'vh' or lfvName =='vg':
            arr=np.array([0.75, 1.00, 1.00, 1.00])
        myfzn=genFN(arr,10, lfvType, lfvName)


        return myfzn