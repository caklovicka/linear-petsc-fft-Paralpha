import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.append('../../..')
import numpy as np
from examples.linear.advection_2d_pbc_upwind5 import Advection as Adv5

prob = Adv5()
N = 700
prob.spatial_points = [N, N]
prob.tol = 1e-12
prob.time_points = 3
prob.proc_col = 1
prob.T_start = 0
prob.T_end = 1.28e-2
prob.solver = 'custom'
prob.maxiter = 10
prob.smaxiter = 50
prob.time_intervals = 64
prob.proc_row = 64
prob.stol = 1e-14

'''
if prob.rolling < 64:
    prob.stol = 1e-15
    prob.tol = 1e-12 / prob.rolling
'''

prob.optimal_alphas = True
#prob.m0 = 10 * (prob.T_end - prob.T_start)/prob.rolling
#prob.optimal_alphas = False
#prob.alphas = [1e-8]

prob.setup()
prob.solve()
prob.summary(details=True)

'''
if prob.rank == prob.size - 1: #prob.size_subcol_seq:
    exact = prob.u_exact(prob.T_end, prob.x).flatten()[prob.row_beg:prob.row_end]
    approx = prob.u_last_loc.flatten()
    d = exact - approx
    d = d.flatten()
    err_abs = np.linalg.norm(d, np.inf)
    # err_abs_root = prob.comm_subcol_seq.reduce(err_abs, op=MPI.MAX, root=prob.size_subcol_seq - 1)
    # if prob.rank == prob.size - 1:
    print('abs err = {}'.format(err_abs))
'''