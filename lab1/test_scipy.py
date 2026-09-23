from scipy.optimize import linear_sum_assignment

mat3 = [[5, 12, 18, 20, 23, 14],
               [10, 9, 6, 12, 15, 11],
               [14, 17, 12, 8, 11, 16],
               [21, 15, 13, 16, 9, 12],
               [12, 10, 14, 18, 22, 7],
               [8, 13, 16, 11, 15, 10]]

row_ind, col_ind = linear_sum_assignment(mat3)
res = sum(mat3[i][col_ind[i]] for i in range(len(mat3)))

print(res)
print(col_ind)