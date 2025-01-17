# the following lines disable the numpy multithreading [optional]
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import sys
sys.path.append('../..')                 # for core
sys.path.append('../../../../../..')     # for jube
import numpy as np
from examples.linear.advection_2d_pbc_upwind5 import Advection as Adv5

prob = Adv5()
N = 700
prob.spatial_points = [N, N]
prob.tol = 1e-12
prob.time_points = 3
prob.proc_col = 1
prob.optimal_alphas = True
prob.T_start = 0
prob.T_end = 1.28e-2 / 100
prob.solver = 'custom'
prob.maxiter = 10
prob.smaxiter = 50

prob.stol = 1e-14
if prob.rolling < 64:
    prob.stol = 1e-15
    prob.tol = 1e-12 / prob.rolling

prob.m0 = 10 * (prob.T_end - prob.T_start)/prob.rolling

prob.setup()
prob.solve()
prob.summary(details=True)
