def NNT(r,s,t):
    return 0.125*(1-r)*(1-s)*(1-t),\
           0.125*(1+r)*(1-s)*(1-t),\
           0.125*(1+r)*(1+s)*(1-t),\
           0.125*(1-r)*(1+s)*(1-t),\
           0.125*(1-r)*(1-s)*(1+t),\
           0.125*(1+r)*(1-s)*(1+t),\
           0.125*(1+r)*(1+s)*(1+t),\
           0.125*(1-r)*(1+s)*(1+t)

def dNNTdr(r,s,t):
    return -0.125*(1-s)*(1-t),\
           +0.125*(1-s)*(1-t),\
           +0.125*(1+s)*(1-t),\
           -0.125*(1+s)*(1-t),\
           -0.125*(1-s)*(1+t),\
           +0.125*(1-s)*(1+t),\
           +0.125*(1+s)*(1+t),\
           -0.125*(1+s)*(1+t)
   
def dNNTds(r,s,t):
    return -0.125*(1-r)*(1-t),\
           -0.125*(1+r)*(1-t),\
           +0.125*(1+r)*(1-t),\
           +0.125*(1-r)*(1-t),\
           -0.125*(1-r)*(1+t),\
           -0.125*(1+r)*(1+t),\
           +0.125*(1+r)*(1+t),\
           +0.125*(1-r)*(1+t)

def dNNTdt(r,s,t):
    return -0.125*(1-r)*(1-s),\
           -0.125*(1+r)*(1-s),\
           -0.125*(1+r)*(1+s),\
           -0.125*(1-r)*(1+s),\
           +0.125*(1-r)*(1-s),\
           +0.125*(1+r)*(1-s),\
           +0.125*(1+r)*(1+s),\
           +0.125*(1-r)*(1+s)


