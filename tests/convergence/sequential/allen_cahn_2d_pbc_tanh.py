import numpy as np
np.set_printoptions(linewidth=np.inf)
import scipy as sp
import matplotlib.pyplot as plt
from seq_time_stepping import Newton, IMEX, Parallel_IMEX_refinement, semi_implicit_refinement, semi_implicit
import seaborn as sns
from time import time
import matplotlib.cm as cm
import seaborn as sns

# ALLEN CAHN
#  GLOBAL VARS
EPS = 0.01
R = 0.25
T1 = 0
steps = 640
T2 =  0.003
dt = (T2 - T1) / steps
X1 = -0.5
X2 = 0.5
coll_points = 2
spatial_points = 350

# tolerances
tol = 1e-5
stol = 1e-6
maxiter = 50

# grid and matrix
x1 = np.linspace(X1, X2, spatial_points + 1)[:-1]
x2 = np.linspace(X1, X2, spatial_points + 1)[:-1]
x = np.meshgrid(x1, x2)
dx = (X2 - X1) / spatial_points

print('dt < EPS ^ 2?', dt < EPS ** 2)
print('dt = ', dt, ', EPS = ', EPS)
print('spatial points = ', spatial_points, ', spatial order = ', dx ** 2, ', dt^(2M-1) = ', dt ** (2 * coll_points - 1))

# initial guess
u0 = np.tanh((R - np.sqrt(x[0] ** 2 + x[1] ** 2)) / (np.sqrt(2) * EPS)).flatten()

# Laplacian 2D and 2nd order
data = 1 / dx ** 2 * np.array([np.ones(spatial_points), -2 * np.ones(spatial_points), np.ones(spatial_points)])
A = sp.sparse.spdiags(data, diags=[-1, 0, 1], m=spatial_points, n=spatial_points)
A = sp.sparse.lil_matrix(A)
A[0, -1] = 1 / dx ** 2
A[-1, 0] = 1 / dx ** 2
A = sp.sparse.kron(A, sp.sparse.eye(spatial_points)) + sp.sparse.kron(sp.sparse.eye(spatial_points), A)


# FUNCTIONS
def F(u):
    return 1 / EPS ** 2 * u * (1 - u ** 2)

def dF(u):
    return 1 / EPS ** 2 * (1 - 3 * u ** 2)

def f(u):
    return A @ u + F(u)

def df(u):
    data = dF(u)
    return A + sp.sparse.spdiags(data, diags=0, m=A.shape[0], n=A.shape[1])

# rhs vector
def b(t):
    return np.zeros(spatial_points ** 2)

'''
# seq. IMEX
print('\nIMEX')
print('====')
t_start = time()
u_imex, res_imex, its_imex = IMEX(T1, u0, dt, F, A, b, steps, restol=tol, stol=stol, coll_points=coll_points, maxiter=maxiter)
print('time = ', time() - t_start)
print('maximum residual = ', max(res_imex))
print('iterations = ', its_imex, ', total = ', sum(its_imex))
'''
'''
# seq. semi-implicit
print('\nsemi-implicit')
print('==========')
t_start = time()
u_si, res_si = semi_implicit(T1, u0, dt, F, A, b, steps, restol=tol, stol=stol, coll_points=coll_points, maxiter=maxiter)
print('time = ', time() - t_start)
print('maximum residual = ', max(res_si))
'''

# seq. Newton
print('\nNewton')
print('========')
t_start = time()
u_newton, res_newton, its_newton = Newton(T1, u0, dt, f, df, b, steps, restol=tol, stol=stol, coll_points=coll_points, maxiter=maxiter)
print('time = ', time() - t_start)
print('maximum residual = ', max(res_newton))
print('iterations = ', its_newton, ', total = ', sum(its_newton))

# plot the solution
u = u_newton.reshape([spatial_points, spatial_points])
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
surf = ax.plot_surface(x[0], x[1], u - u0.reshape([spatial_points, spatial_points]), cmap=cm.coolwarm, linewidth=0, antialiased=False)
#surf = ax.plot_surface(x[0], x[1], u0.reshape([spatial_points, spatial_points]), cmap=cm.coolwarm, linewidth=0, antialiased=False, vmin=-1, vmax=1)

# Customize the z axis.
#ax.set_zlim(-1.01 * dt, 1.01 * dt)
#ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter('{x:.02f}')
ax.set_xlabel('x', fontsize=15)
ax.set_ylabel('y', fontsize=15)


# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.6, aspect=10, location='left')
plt.tight_layout()
plt.show()









