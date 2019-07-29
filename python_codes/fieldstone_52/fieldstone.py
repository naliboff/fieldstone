import sys as sys
import numpy as np
import time as timing
import scipy.sparse as sps
from scipy.sparse.linalg.dsolve import linsolve
from scipy.sparse import lil_matrix

#------------------------------------------------------------------------------

def NNV(r,s):
    if serendipity==1:
       return (1-r)*(1-s)*(-r-s-1)*0.25,\
              (1+r)*(1-s)*(r-s-1) *0.25,\
              (1+r)*(1+s)*(r+s-1) *0.25,\
              (1-r)*(1+s)*(-r+s-1)*0.25,\
              (1-r**2)*(1-s)  *0.5,\
              (1+r)*(1-s**2)*0.5,\
              (1-r**2)*(1+s)  *0.5,\
              (1-r)*(1-s**2)*0.5
    else:
       NV_0= 0.5*rq*(rq-1.) * 0.5*sq*(sq-1.)
       NV_1= 0.5*rq*(rq+1.) * 0.5*sq*(sq-1.)
       NV_2= 0.5*rq*(rq+1.) * 0.5*sq*(sq+1.)
       NV_3= 0.5*rq*(rq-1.) * 0.5*sq*(sq+1.)
       NV_4=     (1.-rq**2) * 0.5*sq*(sq-1.)
       NV_5= 0.5*rq*(rq+1.) *     (1.-sq**2)
       NV_6=     (1.-rq**2) * 0.5*sq*(sq+1.)
       NV_7= 0.5*rq*(rq-1.) *     (1.-sq**2)
       NV_8=     (1.-rq**2) *     (1.-sq**2)
       return NV_0,NV_1,NV_2,NV_3,NV_4,NV_5,NV_6,NV_7,NV_8

def dNNVdr(r,s):
    if serendipity==1:
       return -0.25*(s-1)*(2*r+s), \
              -0.25*(s-1)*(2*r-s), \
              0.25*(s+1)*(2*r+s),  \
              0.25*(s+1)*(2*r-s),  \
              r*(s-1),             \
              0.5*(1-s**2),        \
              -r*(s+1),            \
              -0.5*(1-s**2)
    else:
       dNVdr_0= 0.5*(2.*rq-1.) * 0.5*sq*(sq-1)
       dNVdr_1= 0.5*(2.*rq+1.) * 0.5*sq*(sq-1)
       dNVdr_2= 0.5*(2.*rq+1.) * 0.5*sq*(sq+1)
       dNVdr_3= 0.5*(2.*rq-1.) * 0.5*sq*(sq+1)
       dNVdr_4=       (-2.*rq) * 0.5*sq*(sq-1)
       dNVdr_5= 0.5*(2.*rq+1.) *    (1.-sq**2)
       dNVdr_6=       (-2.*rq) * 0.5*sq*(sq+1)
       dNVdr_7= 0.5*(2.*rq-1.) *    (1.-sq**2)
       dNVdr_8=       (-2.*rq) *    (1.-sq**2)
       return dNVdr_0,dNVdr_1,dNVdr_2,dNVdr_3,dNVdr_4,dNVdr_5,dNVdr_6,dNVdr_7,dNVdr_8

def dNNVds(r,s):
    if serendipity==1:
       return -0.25*(r-1)*(r+2*s), \
              -0.25*(r+1)*(r-2*s), \
              0.25*(r+1)*(r+2*s),  \
              0.25*(r-1)*(r-2*s),  \
              -0.5*(1-r**2),      \
              -(r+1)*s,           \
              0.5*(1-r**2),       \
              (r-1)*s
    else:
       dNVds_0= 0.5*rq*(rq-1.) * 0.5*(2.*sq-1.)
       dNVds_1= 0.5*rq*(rq+1.) * 0.5*(2.*sq-1.)
       dNVds_2= 0.5*rq*(rq+1.) * 0.5*(2.*sq+1.)
       dNVds_3= 0.5*rq*(rq-1.) * 0.5*(2.*sq+1.)
       dNVds_4=     (1.-rq**2) * 0.5*(2.*sq-1.)
       dNVds_5= 0.5*rq*(rq+1.) *       (-2.*sq)
       dNVds_6=     (1.-rq**2) * 0.5*(2.*sq+1.)
       dNVds_7= 0.5*rq*(rq-1.) *       (-2.*sq)
       dNVds_8=     (1.-rq**2) *       (-2.*sq)
       return dNVds_0,dNVds_1,dNVds_2,dNVds_3,dNVds_4,dNVds_5,dNVds_6,dNVds_7,dNVds_8

def NNP(r,s):
    return 0.25*(1-r)*(1-s),\
           0.25*(1+r)*(1-s),\
           0.25*(1+r)*(1+s),\
           0.25*(1-r)*(1+s)

#------------------------------------------------------------------------------

def bx(x, y):
    val=((12.-24.*y)*x**4+(-24.+48.*y)*x*x*x +
         (-48.*y+72.*y*y-48.*y*y*y+12.)*x*x +
         (-2.+24.*y-72.*y*y+48.*y*y*y)*x +
         1.-4.*y+12.*y*y-8.*y*y*y)
    return val

def by(x, y):
    val=((8.-48.*y+48.*y*y)*x*x*x+
         (-12.+72.*y-72.*y*y)*x*x+
         (4.-24.*y+48.*y*y-48.*y*y*y+24.*y**4)*x -
         12.*y*y+24.*y*y*y-12.*y**4)
    return val

def velocity_x(x,y):
    val=x*x*(1.-x)**2*(2.*y-6.*y*y+4*y*y*y)
    return val

def velocity_y(x,y):
    val=-y*y*(1.-y)**2*(2.*x-6.*x*x+4*x*x*x)
    return val

def pressure(x,y):
    val=x*(1.-x)-1./6.
    return val

#------------------------------------------------------------------------------

ndim=2
ndofV=2
ndofP=1

Lx=1.
Ly=1.

if int(len(sys.argv) == 5):
   nelx = int(sys.argv[1])
   nely = int(sys.argv[2])
   visu = int(sys.argv[3])
   serendipity = int(sys.argv[4])
else:
   nelx = 4
   nely = 3
   visu = 1
   serendipity=0

nel=nelx*nely

if serendipity==1:
   NV=(nelx+1)*(nely+1)+nelx*(nely+1)+ (nelx+1)*nely
   mV=8
   mP=4
else:
   NV=(2*nelx+1)*(2*nely+1)
   mV=9
   mP=4

NP=(nelx+1)*(nely+1)
NfemV=NV*ndofV
NfemP=NP*ndofP
Nfem=NfemV+NfemP

hx=Lx/nelx
hy=Ly/nely

print('nelx',nelx)
print('nely',nely)
print('nel ',nel)
print('NV  ',NV)
print('NP     =',NP)
print('NfemV =',NfemV)
print('NfemP =',NfemP)

nqperdim=3
qcoords=[-np.sqrt(3./5.),0.,np.sqrt(3./5.)]
qweights=[5./9.,8./9.,5./9.]

eps=1e-8
eta=1.

sparse=False

if serendipity==1:
   rVnodes=[-1,1,1,-1,0,1,0,-1]
   sVnodes=[-1,-1,1,1,-1,0,1,0]
else:
   rVnodes=[-1,0,+1,-1,0,+1,-1,0,+1]
   sVnodes=[-1,-1,-1,0,0,0,+1,+1,+1]

#################################################################
# grid point setup
#################################################################
start = timing.time()

xV = np.empty(NV,dtype=np.float64)  # x coordinates
yV = np.empty(NV,dtype=np.float64)  # y coordinates

if serendipity==1:
   counter = 0
   for j in range(0,nely+1):
       for i in range(0,nelx+1):
           xV[counter]=i*hx
           yV[counter]=j*hy
           counter += 1

   for j in range(nely):
       for i in range(0,nelx):
           xV[counter]=i*hx+hx/2
           yV[counter]=j*hy
           counter+=1
       for i in range(0,nelx+1):
           xV[counter]=i*hx
           yV[counter]=j*hy+hy/2
           counter+=1

   for i in range(0,nelx):
       xV[counter]=i*hx+hx/2
       yV[counter]=nely*hy
       counter+=1

else:

   counter = 0
   for j in range(0, 2*nely+1):
       for i in range(0, 2*nelx+1):
           xV[counter]=i*hx/2.
           yV[counter]=j*hy/2.
           counter += 1

np.savetxt('gridV.ascii',np.array([xV,yV]).T,header='# x,y')

print("setup: grid points: %.3f s" % (timing.time() - start))

#################################################################
# connectivity
#################################################################
start = timing.time()

iconV=np.zeros((mV,nel),dtype=np.int32)

if serendipity==1:
   counter = 0
   for j in range(0,nely):
       for i in range(0,nelx):
           iconV[0,counter] = i + j * (nelx + 1)
           iconV[1,counter] = i + 1 + j * (nelx + 1)
           iconV[2,counter] = i + 1 + (j + 1) * (nelx + 1)
           iconV[3,counter] = i + (j + 1) * (nelx + 1)
           iconV[4,counter] = (nelx+1)*(nely+1)+i +(2*nelx+1)*j
           iconV[5,counter] = (nelx+1)*(nely+1)+i +(2*nelx+1)*j + (nelx+1)
           iconV[6,counter] = (nelx+1)*(nely+1)+i +(2*nelx+1)*(j+1) 
           iconV[7,counter] = (nelx+1)*(nely+1)+i +(2*nelx+1)*j + (nelx+1)-1
           counter += 1
else:
   nnx=2*nelx+1
   nny=2*nely+1
   counter = 0
   for j in range(0,nely):
       for i in range(0,nelx):
           iconV[0,counter]=(i)*2+1+(j)*2*nnx -1
           iconV[1,counter]=(i)*2+3+(j)*2*nnx -1
           iconV[2,counter]=(i)*2+3+(j)*2*nnx+nnx*2 -1
           iconV[3,counter]=(i)*2+1+(j)*2*nnx+nnx*2 -1
           iconV[4,counter]=(i)*2+2+(j)*2*nnx -1
           iconV[5,counter]=(i)*2+3+(j)*2*nnx+nnx -1
           iconV[6,counter]=(i)*2+2+(j)*2*nnx+nnx*2 -1
           iconV[7,counter]=(i)*2+1+(j)*2*nnx+nnx -1
           iconV[8,counter]=(i)*2+2+(j)*2*nnx+nnx -1
           counter += 1

for iel in range (0,nel):
     print ("iel=",iel)
     for i in range(0,mV):
         print ("node ",i,':',iconV[i,iel],"at pos.",xV[iconV[i,iel]], yV[iconV[i,iel]])


#################################################################
# build pressure grid and iconP 
#################################################################
start = timing.time()

xP=np.empty(NP,dtype=np.float64)     # x coordinates
yP=np.empty(NP,dtype=np.float64)     # y coordinates
iconP=np.zeros((mP,nel),dtype=np.int32)


if serendipity:
   iconP[0:mP,0:nel]=iconV[0:mP,0:nel]
   xP[0:NP]=xV[0:NP]
   yP[0:NP]=yV[0:NP]
else:
   counter = 0
   for j in range(0,nely):
       for i in range(0,nelx):
           iconP[0,counter]=i+j*(nelx+1)
           iconP[1,counter]=i+1+j*(nelx+1)
           iconP[2,counter]=i+1+(j+1)*(nelx+1)
           iconP[3,counter]=i+(j+1)*(nelx+1)
           counter += 1
   counter = 0
   for j in range(0,nely+1):
       for i in range(0,nelx+1):
           xP[counter]=i*hx
           yP[counter]=j*hy
           counter += 1


np.savetxt('gridP.ascii',np.array([xP,yP]).T,header='# x,y')

print("build P grid: %.3f s" % (timing.time() - start))

#################################################################
# compute area of elements
#################################################################
start = timing.time()

area    = np.zeros(nel,dtype=np.float64) 
dNNNVdr = np.zeros(mV,dtype=np.float64)  # shape functions derivatives
dNNNVds = np.zeros(mV,dtype=np.float64)  # shape functions derivatives

for iel in range(0,nel):
    for iq in range(0,nqperdim):
        for jq in range(0,nqperdim):
            rq=qcoords[iq]
            sq=qcoords[jq]
            weightq=qweights[iq]*qweights[jq]
            dNNNVdr[0:mV]=dNNVdr(rq,sq)
            dNNNVds[0:mV]=dNNVds(rq,sq)
            jcb=np.zeros((ndim,ndim),dtype=np.float64)
            for k in range(0,mV):
                jcb[0,0] += dNNNVdr[k]*xV[iconV[k,iel]]
                jcb[0,1] += dNNNVdr[k]*yV[iconV[k,iel]]
                jcb[1,0] += dNNNVds[k]*xV[iconV[k,iel]]
                jcb[1,1] += dNNNVds[k]*yV[iconV[k,iel]]
            jcob = np.linalg.det(jcb)
            area[iel]+=jcob*weightq

print("     -> area (m,M) %.4e %.4e " %(np.min(area),np.max(area)))
print("     -> total area %.6f " %(area.sum()))

print("compute elements areas: %.3f s" % (timing.time() - start))

#################################################################
# define boundary conditions
#################################################################
start = timing.time()

bc_fix = np.zeros(NfemV, dtype=np.bool)  # boundary condition, yes/no
bc_val = np.zeros(NfemV, dtype=np.float64)  # boundary condition, value

for i in range(0,NV):
    if xV[i]<eps:
       bc_fix[i*ndofV]   = True ; bc_val[i*ndofV]   = 0.
       bc_fix[i*ndofV+1] = True ; bc_val[i*ndofV+1] = 0.
    if xV[i]>(Lx-eps):
       bc_fix[i*ndofV]   = True ; bc_val[i*ndofV]   = 0.
       bc_fix[i*ndofV+1] = True ; bc_val[i*ndofV+1] = 0.
    if yV[i]<eps:
       bc_fix[i*ndofV]   = True ; bc_val[i*ndofV]   = 0.
       bc_fix[i*ndofV+1] = True ; bc_val[i*ndofV+1] = 0.
    if yV[i]>(Ly-eps):
       bc_fix[i*ndofV]   = True ; bc_val[i*ndofV]   = 0.
       bc_fix[i*ndofV+1] = True ; bc_val[i*ndofV+1] = 0.

print("setup: boundary conditions: %.3f s" % (timing.time() - start))

#################################################################
# build FE matrix
# [ K G ][u]=[f]
# [GT 0 ][p] [h]
#################################################################
start = timing.time()

if sparse:
   A_sparse = lil_matrix((Nfem,Nfem),dtype=np.float64)
else:   
   K_mat = np.zeros((NfemV,NfemV),dtype=np.float64) # matrix K 
   G_mat = np.zeros((NfemV,NfemP),dtype=np.float64) # matrix GT

f_rhs   = np.zeros(NfemV,dtype=np.float64)        # right hand side f 
h_rhs   = np.zeros(NfemP,dtype=np.float64)        # right hand side h 
b_mat   = np.zeros((3,ndofV*mV),dtype=np.float64) # gradient matrix B 
N_mat   = np.zeros((3,ndofP*mP),dtype=np.float64) # matrix  
NNNV    = np.zeros(mV,dtype=np.float64)           # shape functions V
NNNP    = np.zeros(mP,dtype=np.float64)           # shape functions P
dNNNVdx = np.zeros(mV,dtype=np.float64)           # shape functions derivatives
dNNNVdy = np.zeros(mV,dtype=np.float64)           # shape functions derivatives
dNNNVdr = np.zeros(mV,dtype=np.float64)           # shape functions derivatives
dNNNVds = np.zeros(mV,dtype=np.float64)           # shape functions derivatives
u       = np.zeros(NV,dtype=np.float64)           # x-component velocity
v       = np.zeros(NV,dtype=np.float64)           # y-component velocity
c_mat   = np.array([[2,0,0],[0,2,0],[0,0,1]],dtype=np.float64) 

for iel in range(0,nel):

    # set arrays to 0 every loop
    f_el =np.zeros((mV*ndofV),dtype=np.float64)
    K_el =np.zeros((mV*ndofV,mV*ndofV),dtype=np.float64)
    G_el=np.zeros((mV*ndofV,mP*ndofP),dtype=np.float64)
    h_el=np.zeros((mP*ndofP),dtype=np.float64)

    for iq in range(0,nqperdim):
        for jq in range(0,nqperdim):
            rq=qcoords[iq]
            sq=qcoords[jq]
            weightq=qweights[iq]*qweights[jq]

            NNNV[0:mV]=NNV(rq,sq)
            dNNNVdr[0:mV]=dNNVdr(rq,sq)
            dNNNVds[0:mV]=dNNVds(rq,sq)
            NNNP[0:mP]=NNP(rq,sq)

            # calculate jacobian matrix
            jcb=np.zeros((ndim,ndim),dtype=np.float64)
            for k in range(0,mV):
                jcb[0,0] += dNNNVdr[k]*xV[iconV[k,iel]]
                jcb[0,1] += dNNNVdr[k]*yV[iconV[k,iel]]
                jcb[1,0] += dNNNVds[k]*xV[iconV[k,iel]]
                jcb[1,1] += dNNNVds[k]*yV[iconV[k,iel]]
            jcob = np.linalg.det(jcb)
            jcbi = np.linalg.inv(jcb)

            # compute dNdx & dNdy
            xq=0.0
            yq=0.0
            for k in range(0,mV):
                xq+=NNNV[k]*xV[iconV[k,iel]]
                yq+=NNNV[k]*yV[iconV[k,iel]]
                dNNNVdx[k]=jcbi[0,0]*dNNNVdr[k]+jcbi[0,1]*dNNNVds[k]
                dNNNVdy[k]=jcbi[1,0]*dNNNVdr[k]+jcbi[1,1]*dNNNVds[k]

            # construct 3x8 b_mat matrix
            for i in range(0,mV):
                b_mat[0:3, 2*i:2*i+2] = [[dNNNVdx[i],0.     ],
                                         [0.        ,dNNNVdy[i]],
                                         [dNNNVdy[i],dNNNVdx[i]]]

            # compute elemental a_mat matrix
            K_el+=b_mat.T.dot(c_mat.dot(b_mat))*eta*weightq*jcob

            # compute elemental rhs vector
            for i in range(0,mV):
                f_el[ndofV*i  ]+=NNNV[i]*jcob*weightq*bx(xq,yq)
                f_el[ndofV*i+1]+=NNNV[i]*jcob*weightq*by(xq,yq)

            for i in range(0,mP):
                N_mat[0,i]=NNNP[i]
                N_mat[1,i]=NNNP[i]
                N_mat[2,i]=0.

            G_el-=b_mat.T.dot(N_mat)*weightq*jcob

        # end for jq
    # end for iq

    # impose b.c. 
    for k1 in range(0,mV):
        for i1 in range(0,ndofV):
            ikk=ndofV*k1          +i1
            m1 =ndofV*iconV[k1,iel]+i1
            if bc_fix[m1]:
               K_ref=K_el[ikk,ikk] 
               for jkk in range(0,mV*ndofV):
                   f_el[jkk]-=K_el[jkk,ikk]*bc_val[m1]
                   K_el[ikk,jkk]=0
                   K_el[jkk,ikk]=0
               K_el[ikk,ikk]=K_ref
               f_el[ikk]=K_ref*bc_val[m1]
               h_el[:]-=G_el[ikk,:]*bc_val[m1]
               G_el[ikk,:]=0

    # assemble matrix K_mat and right hand side rhs
    for k1 in range(0,mV):
        for i1 in range(0,ndofV):
            ikk=ndofV*k1          +i1
            m1 =ndofV*iconV[k1,iel]+i1
            for k2 in range(0,mV):
                for i2 in range(0,ndofV):
                    jkk=ndofV*k2          +i2
                    m2 =ndofV*iconV[k2,iel]+i2
                    if sparse:
                       A_sparse[m1,m2] += K_el[ikk,jkk]
                    else:
                       K_mat[m1,m2]+=K_el[ikk,jkk]
            for k2 in range(0,mP):
                jkk=k2
                m2 =iconP[k2,iel]
                if sparse:
                   A_sparse[m1,NfemV+m2]+=G_el[ikk,jkk]
                   A_sparse[NfemV+m2,m1]+=G_el[ikk,jkk]
                else:
                   G_mat[m1,m2]+=G_el[ikk,jkk]
            f_rhs[m1]+=f_el[ikk]
    for k2 in range(0,mP):
        m2=iconP[k2,iel]
        h_rhs[m2]+=h_el[k2]

if not sparse:
   print("     -> K_mat (m,M) %.4f %.4f " %(np.min(K_mat),np.max(K_mat)))
   print("     -> G_mat (m,M) %.4f %.4f " %(np.min(G_mat),np.max(G_mat)))

print("build FE matrix: %.3fs - %d elts" % (timing.time()-start, nel))

######################################################################
# assemble K, G, GT, f, h into A and rhs
######################################################################
start = timing.time()

rhs = np.zeros(Nfem,dtype=np.float64)         # right hand side of Ax=b
rhs[0:NfemV]=f_rhs
rhs[NfemV:Nfem]=h_rhs

if not sparse:
   a_mat = np.zeros((Nfem,Nfem),dtype=np.float64) 
   a_mat[0:NfemV,0:NfemV]=K_mat
   a_mat[0:NfemV,NfemV:Nfem]=G_mat
   a_mat[NfemV:Nfem,0:NfemV]=G_mat.T

print("assemble blocks: %.3f s" % (timing.time() - start))

######################################################################
# assign extra pressure b.c. to remove null space
######################################################################

if sparse:
   A_sparse[Nfem-1,:]=0
   A_sparse[:,Nfem-1]=0
   A_sparse[Nfem-1,Nfem-1]=1
   rhs[Nfem-1]=0
else:
   a_mat[Nfem-1,:]=0
   a_mat[:,Nfem-1]=0
   a_mat[Nfem-1,Nfem-1]=1
   rhs[Nfem-1]=0

######################################################################
# solve system
######################################################################
start = timing.time()

if sparse:
   sparse_matrix=A_sparse.tocsr()
else:
   sparse_matrix=sps.csr_matrix(a_mat)

sol=sps.linalg.spsolve(sparse_matrix,rhs)

print("solve time: %.3f s" % (timing.time() - start))

######################################################################
# put solution into separate x,y velocity arrays
######################################################################
start = timing.time()

u,v=np.reshape(sol[0:NfemV],(NV,2)).T
p=sol[NfemV:Nfem]

print("     -> u (m,M) %.4f %.4f " %(np.min(u),np.max(u)))
print("     -> v (m,M) %.4f %.4f " %(np.min(v),np.max(v)))
print("     -> p (m,M) %.4f %.4f " %(np.min(p),np.max(p)))

np.savetxt('velocity.ascii',np.array([xV,yV,u,v]).T,header='# x,y,u,v')
np.savetxt('pressure.ascii',np.array([xP,yP,p]).T,header='# x,y,p')

print("split vel into u,v: %.3f s" % (timing.time() - start))

#####################################################################
# normalise pressure field 
#####################################################################

avrg_p=0.
for iel in range(0,nel):
    for iq in range(0,nqperdim):
        for jq in range(0,nqperdim):
            rq=qcoords[iq]
            sq=qcoords[jq]
            weightq=qweights[iq]*qweights[jq]
            NNNP[0:mP]=NNP(rq,sq)

            # compure pressure at q point
            pq=0.
            for k in range(0,mP):
                pq+=NNNP[k]*p[iconP[k,iel]]

            # calculate jacobian matrix
            jcb=np.zeros((ndim,ndim),dtype=np.float64)
            for k in range(0,mV):
                jcb[0,0] += dNNNVdr[k]*xV[iconV[k,iel]]
                jcb[0,1] += dNNNVdr[k]*yV[iconV[k,iel]]
                jcb[1,0] += dNNNVds[k]*xV[iconV[k,iel]]
                jcb[1,1] += dNNNVds[k]*yV[iconV[k,iel]]
            jcob = np.linalg.det(jcb)

            avrg_p+=pq*jcob*weightq

print('avrg pressure',avrg_p)

p[:]-=avrg_p

np.savetxt('pressure.ascii',np.array([xP,yP,p]).T,header='# x,y,p')

#####################################################################
# project pressure onto velocity grid
#####################################################################
start = timing.time()

q=np.zeros(NV,dtype=np.float64)
c=np.zeros(NV,dtype=np.float64)

for iel in range(0,nel):
    for i in range(0,mV):
        NNNP[0:mP]=NNP(rVnodes[i],sVnodes[i])
        q[iconV[i,iel]]+=np.dot(p[iconP[0:mP,iel]],NNNP[0:mP])
        c[iconV[i,iel]]+=1.
    # end for i
# end for iel

q=q/c

np.savetxt('q.ascii',np.array([xV,yV,q]).T,header='# x,y,q')

print("project p onto Vnodes: %.3f s" % (timing.time() - start))

#####################################################################
# compute L2 errors
#####################################################################
start = timing.time()

errv=0.
errp=0.
errq=0.
for iel in range (0,nel):

    for iq in range(0,nqperdim):
        for jq in range(0,nqperdim):
            rq=qcoords[iq]
            sq=qcoords[jq]
            weightq=qweights[iq]*qweights[jq]

            NNNV[0:mV]=NNV(rq,sq)
            dNNNVdr[0:mV]=dNNVdr(rq,sq)
            dNNNVds[0:mV]=dNNVds(rq,sq)
            NNNP[0:mP]=NNP(rq,sq)

            jcb=np.zeros((ndim,ndim),dtype=np.float64)
            for k in range(0,mV):
                jcb[0,0] += dNNNVdr[k]*xV[iconV[k,iel]]
                jcb[0,1] += dNNNVdr[k]*yV[iconV[k,iel]]
                jcb[1,0] += dNNNVds[k]*xV[iconV[k,iel]]
                jcb[1,1] += dNNNVds[k]*yV[iconV[k,iel]]
            jcob = np.linalg.det(jcb)
            jcbi = np.linalg.inv(jcb)

            xq=0.
            yq=0.
            uq=0.
            vq=0.
            qq=0.
            for k in range(0,mV):
                xq+=NNNV[k]*xV[iconV[k,iel]]
                yq+=NNNV[k]*yV[iconV[k,iel]]
                uq+=NNNV[k]*u[iconV[k,iel]]
                vq+=NNNV[k]*v[iconV[k,iel]]
                qq+=NNNV[k]*q[iconV[k,iel]]
            errv+=((uq-velocity_x(xq,yq))**2+(vq-velocity_y(xq,yq))**2)*weightq*jcob
            errq+=(qq-pressure(xq,yq))**2*weightq*jcob

            xq=0.
            yq=0.
            pq=0.
            for k in range(0,mP):
                xq+=NNNP[k]*xP[iconP[k,iel]]
                yq+=NNNP[k]*yP[iconP[k,iel]]
                pq+=NNNP[k]*p[iconP[k,iel]]
            errp+=(pq-pressure(xq,yq))**2*weightq*jcob

        # end for jq
    # end for iq
# end for iel

errv=np.sqrt(errv)
errp=np.sqrt(errp)
errq=np.sqrt(errq)

print("     -> nel= %6d ; errv= %.8e ; errp= %.8e ; errq= %.8e" %(nel,errv,errp,errq))

print("compute errors: %.3f s" % (timing.time() - start))

#####################################################################
# plot of solution
#####################################################################

if visu==1:
    vtufile=open('solution.vtu',"w")
    vtufile.write("<VTKFile type='UnstructuredGrid' version='0.1' byte_order='BigEndian'> \n")
    vtufile.write("<UnstructuredGrid> \n")
    vtufile.write("<Piece NumberOfPoints=' %5d ' NumberOfCells=' %5d '> \n" %(NV,nel))
    #####
    vtufile.write("<Points> \n")
    vtufile.write("<DataArray type='Float32' NumberOfComponents='3' Format='ascii'> \n")
    for i in range(0,NV):
        vtufile.write("%10e %10e %10e \n" %(xV[i],yV[i],0.))
    vtufile.write("</DataArray>\n")
    vtufile.write("</Points> \n")
    #####
    #vtufile.write("<CellData Scalars='scalars'>\n")
    #--
    #vtufile.write("<DataArray type='Float32' Name='area' Format='ascii'> \n")
    #for iel in range (0,nel):
    #    vtufile.write("%10e\n" % (area[iel]))
    #vtufile.write("</DataArray>\n")
    #--
    #vtufile.write("<DataArray type='Float32' Name='exx' Format='ascii'> \n")
    #for iel in range (0,nel):
    #    vtufile.write("%10e\n" % (exx[iel]))
    #vtufile.write("</DataArray>\n")
    #vtufile.write("<DataArray type='Float32' Name='eyy' Format='ascii'> \n")
    #for iel in range (0,nel):
    #    vtufile.write("%10e\n" % (eyy[iel]))
    #vtufile.write("</DataArray>\n")
    #vtufile.write("<DataArray type='Float32' Name='exy' Format='ascii'> \n")
    #for iel in range (0,nel):
    #    vtufile.write("%10e\n" % (exy[iel]))
    #vtufile.write("</DataArray>\n")
    #vtufile.write("</CellData>\n")
    #####
    vtufile.write("<PointData Scalars='scalars'>\n")
    #--
    vtufile.write("<DataArray type='Float32' NumberOfComponents='3' Name='velocity' Format='ascii'> \n")
    for i in range(0,NV):
        vtufile.write("%10e %10e %10e \n" %(u[i],v[i],0.))
    vtufile.write("</DataArray>\n")
    #--
    vtufile.write("<DataArray type='Float32' Name='q' Format='ascii'> \n")
    for i in range(0,NV):
        vtufile.write("%10e \n" %q[i])
    vtufile.write("</DataArray>\n")
    #--
    #vtufile.write("<DataArray type='Float32' Name='error u' Format='ascii'> \n")
    #for i in range(0,NV):
    #    vtufile.write("%.5e \n" %error_u[i])
    #vtufile.write("</DataArray>\n")
    #--
    #vtufile.write("<DataArray type='Float32' Name='error v' Format='ascii'> \n")
    #for i in range(0,NV):
    #    vtufile.write("%.5e \n" %error_v[i])
    #vtufile.write("</DataArray>\n")
    #--
    #vtufile.write("<DataArray type='Float32' Name='error q' Format='ascii'> \n")
    #for i in range(0,NV):
    #    vtufile.write("%.5e \n" %error_q[i])
    #vtufile.write("</DataArray>\n")
    #--
    vtufile.write("</PointData>\n")
    #####
    vtufile.write("<Cells>\n")
    #--
    vtufile.write("<DataArray type='Int32' Name='connectivity' Format='ascii'> \n")
    for iel in range (0,nel):
        vtufile.write("%d %d %d %d %d %d %d %d \n" %(iconV[0,iel],iconV[1,iel],\
                                                     iconV[2,iel],iconV[3,iel],\
                                                     iconV[4,iel],iconV[5,iel],\
                                                     iconV[6,iel],iconV[7,iel]))
    vtufile.write("</DataArray>\n")
    #--
    vtufile.write("<DataArray type='Int32' Name='offsets' Format='ascii'> \n")
    for iel in range (0,nel):
        vtufile.write("%d \n" %((iel+1)*mV))
    vtufile.write("</DataArray>\n")
    #--
    vtufile.write("<DataArray type='Int32' Name='types' Format='ascii'>\n")
    for iel in range (0,nel):
        vtufile.write("%d \n" %23)
    vtufile.write("</DataArray>\n")
    #--
    vtufile.write("</Cells>\n")
    #####
    vtufile.write("</Piece>\n")
    vtufile.write("</UnstructuredGrid>\n")
    vtufile.write("</VTKFile>\n")
    vtufile.close()

print("-----------------------------")
print("------------the end----------")
print("-----------------------------")