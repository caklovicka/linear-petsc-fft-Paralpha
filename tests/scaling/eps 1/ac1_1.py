# the following lines disable the numpy multithreading [optional]
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.append('../../..')                 # for core
sys.path.append('../../../../../../..')     # for jube
import numpy as np

# time steps: 64
# rolling from runtime
# time_intervals from runtime
# beta from runtime

from examples.nonlinear.allen_cahn_2d_pbc_central4 import AllenCahn
prob = AllenCahn()
prob.spatial_points = [200, 200]
prob.time_points = 2
prob.tol = 1e-5
prob.stol = 1e-7

prob.eps = 1
prob.T_start = 0
prob.proc_col = 1
prob.solver = 'gmres'
prob.maxiter = 20
prob.smaxiter = 500
prob.alphas = [1e-8]
prob.R = 2
prob.X_left = -2 * prob.R
prob.X_right = 2 * prob.R
prob.Y_left = -2 * prob.R
prob.Y_right = 2 * prob.R
prob.T_end = 1

prob.proc_row = prob.time_intervals

prob.setup()
print(prob.T_end, prob.dx[0]**4, prob.dt**(2 * prob.time_points - 1), prob.dt < prob.eps**2)
print(prob.eps, prob.eps**2, prob.eps**3)
prob.solve()
prob.summary(details=False)

