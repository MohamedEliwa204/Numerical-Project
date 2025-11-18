# 0-based index
import numpy as np


def partial_pivoting(A,b,k):
    n = A.shape[0]
    max_index = k
    for i in range(k,n):
        if abs(A[i][k]) > abs(A[max_index][k]):
            max_index = i

    if max_index != k:
        A[[k, max_index]] = A[[max_index, k]]
        b[[k, max_index]] = b[[max_index, k]]

def forward_elimination(A,b):
    n = A.shape[0]
    for k in range(0, n-1):   # row traverse(find the row to pivot)
        partial_pivoting(A,b,k)
        for i in range(k + 1, n):  #row traverse(apply the elimination for specific row)
            factor = A[i][k]/A[k][k]
            for j in range(k, n):  # column traverse(apply the elimination for each element in this row)
                A[i][j] = A[i][j] - (factor * A[k][j])
            b[i] = b[i] - (factor * b[k])




def forward_substitution(A,b):
    n = A.shape[0]
    x = np.zeros(n)
    x[0] = b[0] / A[0][0]
    for i in range (1, n): # row traverse forward
        sum = 0
        for j in range(0, i): # column traverse backward
            sum = sum + (x[j] * A[i][j])

        x[i] = (b[i] - sum) / A[i][i]

    return x


def backward_substitution(A,b):
    n = A.shape[0]
    x = np.zeros(n)
    x[n - 1] = b[n - 1] / A[n-1][n-1]
    for i in range(n - 2, -1, -1):  # row traverse backward
        sum = 0
        for j in range(i + 1, n):  # column traverse forward
            sum = sum + (x[j] * A[i][j])

        x[i] = (b[i] - sum) / A[i][i]

    return x
