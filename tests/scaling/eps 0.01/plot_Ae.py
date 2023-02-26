import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

K = 1
mksz=20
col = sns.color_palette("bright", 2 * K)

legend = []
imex_proc = []
imex_time = []
imex_its = []
newton_proc = []
newton_time = []
newton_its = []

for k in range(K):
    # beta | nproc | time | tot iters | convergence | diff
    table = np.loadtxt('output{}/000000/result/result.dat'.format(k + 1), delimiter='|', skiprows=3, usecols=[1, 2, 5, 8, 12, 13])
    table2 = np.loadtxt('output{}/000001/result/result.dat'.format(k + 1), delimiter='|', skiprows=3, usecols=[1, 2, 5, 8, 12])

    legend.append('imex ' + str(k + 1))
    legend.append('newton ' + str(k + 1))

    imex_proc.append([])
    imex_time.append([])
    imex_its.append([])
    newton_proc.append([])
    newton_time.append([])
    newton_its.append([])

    for i in range(table.shape[0]):

        rolling = 64 / table[i, 1]
        #rolling = 1

        if table[i, 0] == 1:
            newton_proc[k].append(np.log2(table[i, 1]))
            newton_time[k].append(table[i, 2])
            newton_its[k].append('$' + str(round(table[i, 3] / rolling)) + '$')

    for i in range(table2.shape[0]):

        if table2[i, 0] == 0:
            imex_proc[k].append(np.log2(table2[i, 1]))
            imex_time[k].append(table2[i, 2])
            imex_its[k].append('$' + str(round(table2[i, 3] / rolling)) + '$')

    plt.semilogy(imex_proc[k], imex_time[k], ':', color=col[k])
    plt.semilogy(newton_proc[k], newton_time[k], '--', color=col[k])

for k in range(K):
    for i in range(len(imex_its[k])):
        plt.semilogy(imex_proc[k][i], imex_time[k][i], marker=imex_its[k][i], color=col[k], markersize=mksz)

    for i in range(len(newton_its[k])):
        plt.semilogy(newton_proc[k][i], newton_time[k][i], marker=newton_its[k][i], color=col[k], markersize=mksz)


plt.legend(legend)
plt.xlabel('cores')
plt.ylabel('time[s]')
#plt.title('eps = 0.01')
plt.grid('gray')
plt.xticks([0, 1, 2, 3, 4, 5, 6], [1, 2, 4, 8, 16, 32, 64])
plt.show()
