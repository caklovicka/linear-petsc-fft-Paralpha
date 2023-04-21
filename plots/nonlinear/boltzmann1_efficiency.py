import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D

legend = []
petsc_proc = []
petsc_time = []
custom_lines = []
mksz = 10
lw = 2
plt.figure(figsize=(7, 6))
col = sns.color_palette("bright", 3)

# just PETSc
# nproc | time
table = np.loadtxt('data/boltzmann1_petsc.dat', delimiter='|', skiprows=3, usecols=[1, 2])
seq_time = table[0, 1]

for i in range(table.shape[0]):
    petsc_proc.append(np.log2(table[i, 0]))
    petsc_time.append(table[i, 1])

all_proc = petsc_proc + [7, 8, 9, 10, 11]
plt.plot(petsc_proc, seq_time / (np.array(petsc_time) * 2**np.array(petsc_proc)), 'X-', color='gray', markersize=mksz, linewidth=lw)

# PinT + PETSc
runs = [16, 32, 64]
K = len(runs)

pint_petsc_proc = []
pint_petsc_time = []
pint_petsc_iters = []

custom_lines.append(Line2D([0], [0], color='gray', linestyle='-'))
custom_lines.append(Line2D([0], [0], color='gray', linestyle=':'))
legend.append('petsc')
legend.append('ideal')

for k in range(K):
    # nproc | proc_col | time | tot iters
    table = np.loadtxt('data/boltzmann1_petsc{}_pint.dat'.format(runs[k]), delimiter='|', skiprows=3, usecols=[1, 2, 5, 8])

    pint_petsc_proc.append([])
    pint_petsc_time.append([])
    pint_petsc_iters.append([])

    proc_col = table[0, 1]
    legend.append('petsc({}) + pint '.format(int(proc_col)))
    custom_lines.append(Line2D([0], [0], color=col[k], linestyle='--'))

    pint_petsc_proc[k].append(np.log2(int(proc_col)))
    petsc_time_seq = petsc_time[int(pint_petsc_proc[k][-1])]
    pint_petsc_time[k].append(petsc_time_seq)
    #pint_petsc_iters[k].append(32)
    pint_petsc_iters[k].append(1)

    for i in range(table.shape[0]):
        pint_petsc_proc[k].append(np.log2(table[i, 0]))
        pint_petsc_time[k].append(table[i, 2])

        # pint_petsc_iters[k].append('$' + str(int(table[i, 3])) + '$')
        rolling = 32 / (table[i, 0] / table[i, 1])
        it = table[i, 3] / rolling
        if float(int(it)) == it:
            it = int(it)
        pint_petsc_iters[k].append(it)

    for i in range(len(pint_petsc_iters[k])):
        plt.plot(pint_petsc_proc[k][i], seq_time / (np.array(pint_petsc_time[k][i]) * 2**np.array(pint_petsc_proc[k][i])), color=col[k], marker='X', markersize=mksz)#marker)

    plt.plot(pint_petsc_proc[k], seq_time / (np.array(pint_petsc_time[k]) * 2**np.array(pint_petsc_proc[k])), linestyle='--', color=col[k], linewidth=lw)

plt.legend(custom_lines, legend)
plt.xlabel('total number of cores', fontsize=12)
plt.ylabel('efficiency', fontsize=12)
plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048])
plt.grid('gray')
plt.tight_layout()
plt.show()