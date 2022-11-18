import numpy as np
from scipy import sparse
from petsc4py import PETSc
from core.imex_newton_increment_paralpha import IMEXNewtonIncrementParalpha

# Julia backend
from julia.api import Julia
jl = Julia(compiled_modules=False)
from julia import KitBase as kt

"""
boltzman equation
u_t + v2 * u_y = Q(u)
"""


class Boltzmann(IMEXNewtonIncrementParalpha):

    # user defined, just for this class
    Y_left = -1
    Y_right = 1

    L = 8
    U_left = -L
    U_right = L
    V_left = -L
    V_right = L
    W_left = -L
    W_right = L

    yy = None
    uu = None
    vv = None
    ww = None

    vs = None
    knudsen = 1e-2
    muref = kt.ref_vhs_vis(knudsen, 1.0, 0.5)
    fsm = None
    gas = None
    phi = None
    psi = None
    chi = None

    # PROCESSORS NEEDED = proc_row * proc_col

    def __init__(self):

        super().__init__()

    def setup(self):

        # ---- PRESETUP ----
        self.vs = kt.VSpace3D(self.U_left, self.U_right, self.spatial_points[1], self.V_left, self.V_right, self.spatial_points[2], self.W_left, self.W_right, self.spatial_points[3])
        self.fsm = kt.fsm_kernel(self.vs, self.muref, 5, 1.0)
        self.gas = kt.Gas(Kn=self.knudsen, K=0.0, fsm=self.fsm)

        self.phi, self.psi, self.chi = kt.kernel_mode(
            5,
            self.vs.u1,
            self.vs.v1,
            self.vs.w1,
            self.vs.du[1, 1, 1],
            self.vs.dv[1, 1, 1],
            self.vs.dw[1, 1, 1],
            self.vs.nu,
            self.vs.nv,
            self.vs.nw,
            1.0,
        )

        self.yy = np.linspace(self.Y_left, self.Y_right, self.spatial_points[0] + 1)[:-1]
        self.uu = np.linspace(self.U_left, self.U_right, self.spatial_points[1] + 1)[:-1]
        self.vv = np.linspace(self.V_left, self.V_right, self.spatial_points[2] + 1)[:-1]
        self.ww = np.linspace(self.W_left, self.W_right, self.spatial_points[3] + 1)[:-1]

        self.dx = []
        self.dx.append((self.Y_right - self.Y_left) / self.spatial_points[0])
        self.dx.append((self.U_right - self.U_left) / self.spatial_points[1])
        self.dx.append((self.V_right - self.V_left) / self.spatial_points[2])
        self.dx.append((self.W_right - self.W_left) / self.spatial_points[3])

        # x and size_global_A have to be filled before super().setup()
        self.x = np.meshgrid(self.yy, self.uu, self.vv, self.ww)
        self.global_size_A = 1
        for n in self.spatial_points:
            self.global_size_A *= n

        # ---- PRESETUP <end> ----

        # do not delete this, this builds communicators needed for your matrix Apar
        super().setup()

        # ---- POSTSETUP ----

        # user defined, parallel matrix, rows are divided between processors in group 'comm_matrix'
        # rows_beg and rows_end define the chunk of matrix Apar in this communicator

        # user defined matrix Apar, sparse form recommended
        row = list()
        col = list()
        data = list()
        Nuvw = self.spatial_points[1] * self.spatial_points[2] * self.spatial_points[3]
        Nvw = self.spatial_points[2] * self.spatial_points[3]
        Nw = self.spatial_points[3]
        for i in range(self.row_beg, self.row_end, 1):

            iv = (i % Nuvw) % Nvw // Nw
            if self.vv[iv] < 0:
                row.append(i)
                col.append(i)
                data.append(-self.vv[iv] / self.dx[0])

                row.append(i)
                col.append((i + Nuvw) % self.global_size_A)
                data.append(self.vv[iv] / self.dx[0])

            else:
                row.append(i)
                col.append(i)
                data.append(self.vv[iv] / self.dx[0])

                row.append(i)
                col.append((i + Nuvw) % self.global_size_A)
                data.append(-self.vv[iv] / self.dx[0])

        data = np.array(data)
        row = np.array(row) - self.row_beg
        col = np.array(col)
        self.Apar = sparse.csr_matrix((data, (row, col)), shape=(self.row_end - self.row_beg, self.global_size_A))
        del data, row, col

        # ---- POSTSETUP <end> ----

    # user defined
    def bpar(self, t):
        return self.rhs(t, self.x).flatten()[self.row_beg:self.row_end]

    def fw(self, x, p):
        ρ = 1 + 0.1 * np.sin(2 * np.pi * x)
        u = 1.0
        λ = ρ
        return kt.prim_conserve([ρ, u, 0, 0, λ], self.gas.γ)

    def ff(self, x, p):
        w = self.fw(x, p)
        prim = kt.conserve_prim(w, self.gas.γ)
        return kt.maxwellian(self.vs.u, self.vs.v, self.vs.w, prim)


    # user defined
    def u_initial(self, z):
        f = np.zeros(self.spatial_points)
        for i in range(self.spatial_points[0]):
            f[i, :, :, :] = self.ff(self.yy[i], None)
        return f

    def F(self, u):
        # not ready for parallel in space or across nodes
        f = u.reshape(self.spatial_points).real
        Q = np.empty_like(f)
        for i in range(self.spatial_points[0]):
            Q[i, :, :, :] = self.dt * kt.boltzmann_fft(f[i, :, :, :], self.gas.fsm.Kn, self.gas.fsm.nm, self.phi, self.psi, self.chi)
        return Q.flatten()

    # user defined
    @staticmethod
    def rhs(t, z):
        return 0 * z[0]

    @staticmethod
    def norm(x):
        return np.linalg.norm(x.real, np.inf)

    # petsc solver on comm_matrix
    def linear_solver(self, M_loc, m_loc, m0_loc, tol):
        m = PETSc.Vec()
        m.createWithArray(array=m_loc, comm=self.comm_matrix)
        m0 = PETSc.Vec()
        m0.createWithArray(array=m0_loc, comm=self.comm_matrix)
        M = PETSc.Mat()
        csr = (M_loc.indptr, M_loc.indices, M_loc.data)
        M.createAIJWithArrays(size=(self.global_size_A, self.global_size_A), csr=csr, comm=self.comm_matrix)

        ksp = PETSc.KSP()
        ksp.create(comm=self.comm_matrix)
        ksp.setType('gmres')
        ksp.setFromOptions()
        ksp.setTolerances(rtol=tol, max_it=self.smaxiter)
        pc = ksp.getPC()
        pc.setType('none')
        ksp.setOperators(M)
        ksp.setInitialGuessNonzero(True)
        ksp.solve(m, m0)
        sol = m0.getArray()
        it = ksp.getIterationNumber()

        m.destroy()
        m0.destroy()
        ksp.destroy()
        M.destroy()
        pc.destroy()

        return sol, it







