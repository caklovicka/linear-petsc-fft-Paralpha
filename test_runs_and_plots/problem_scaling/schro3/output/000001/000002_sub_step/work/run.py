import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.append('../../../../../../..')    # for jube
sys.path.append('../../../../../../../..')    # for pySDC
import numpy as np
from problem_examples_parallel.schrodinger_2d_0_central6 import Schrodinger as Schro6

prob = Schro6()
N = 1200
prob.spatial_points = [N, N]
prob.tol = 1e-12
prob.proc_col = 1
prob.time_points = 3
prob.optimal_alphas = True
prob.T_start = 0
prob.solver = 'custom'
prob.maxiter = 10
prob.smaxiter = 50
prob.stol = 1e-13
if prob.rolling == 1:
    prob.stol /= 100

prob.m0 = 10 * (prob.T_end - prob.T_start)/prob.rolling

prob.setup()
prob.solve()
prob.summary(details=True)

if prob.rank == prob.size - 1:
    exact = prob.u_exact(prob.T_end, prob.x).flatten()[prob.row_beg:prob.row_end]
    approx = prob.u_last_loc.flatten()
    d = exact - approx
    d = d.flatten()
    err_abs = np.linalg.norm(d, np.inf)
    print('abs err = {}'.format(err_abs))


