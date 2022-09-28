import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D

path = ['adv1_strong/output/000010/result/result.dat', 'adv2_strong/output/000006/result/result.dat', 'adv3_strong/output/000007/result/result.dat']

# nproc | tot_time | iters
eq = []
for p in path:
    eq.append(np.loadtxt(p, delimiter='|', usecols=[0, 3, 7], skiprows=3))

petsc_run = np.loadtxt('adv1_strong/output/000011/result/result.dat', delimiter='|', usecols=[0, 3], skiprows=3)
ticks = []
labels = []
n = eq[0].shape[0]
seqT = [10.364230, 34.768069, 108.604033]   # from --id=5,3,4
marks = 16
lw = 2
linst = ['dotted', 'dashed', 'dashdot']
custom_lines = []
col = sns.color_palette("bright", len(eq))

indices = np.argsort(petsc_run[:, 0])
petsc_run = petsc_run[indices, :]
petsc_run[:, 1] = petsc_run[0, 1] / petsc_run[:, 1]

plt.plot(np.log2(petsc_run[:, 0]), petsc_run[:, 1], linestyle='-', linewidth=lw, color='silver', marker='D', markersize=marks//2)
ticks += list(np.log2(petsc_run[:, 0]))
labels += list(petsc_run[:, 0])

for i in range(len(eq)):
    eq[i][:, 1] = seqT[i] / eq[i][:, 1]
    indices = np.argsort(eq[i][:, 0])
    eq[i] = eq[i][indices, :]

    # connect points with petsc runs
    if i > 0:
        plt.plot(np.log2(np.array([12, eq[i][0, 0]])), [petsc_run[4, 1], eq[i][0, 1]], linestyle=linst[i], linewidth=lw, color='silver', markersize=marks // 2)

    plt.plot(np.log2(eq[i][:, 0]), eq[i][:, 1], linestyle=linst[i], linewidth=lw, color=col[i])
    custom_lines.append(Line2D([0], [0], linestyle=linst[i], linewidth=lw, color=col[i]))
    ticks += list(np.log2(eq[i][:, 0]))
    labels += list(eq[i][:, 0])

for i in range(len(eq)):
    for nn in range(n):
        m = int(eq[i][nn, 2])
        plt.plot(np.log2(eq[i][nn, 0]), eq[i][nn, 1], marker="$" + str(m) + "$", markersize=marks, color=col[i])

labels = [int(l) for l in labels]
plt.xticks(ticks, labels, rotation=70)
plt.tick_params(labelsize=12)
names = ['1e-5, M=1', '1e-9, M=2', '1e-12, M=3', 'petsc4py', 'k iterations']
custom_lines.append(Line2D([0], [0], linestyle='-', linewidth=lw, color='gray', marker='D', markersize=marks//2))
custom_lines.append(Line2D([0], [0], marker="$k$", markersize=10, color='gray'))
plt.legend(custom_lines, names, loc='upper left')
plt.grid(True)
plt.ylabel('speedup')
plt.xlabel('number of cores')
# plt.xlim([0, 5])
# plt.ylim([0, 15])
plt.show()