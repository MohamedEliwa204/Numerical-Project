def partial_pivoting(A,b,k):
    n = A.shape[0]
    max_index = k
    for i in range(k,n):
        if abs(A[i][k] > abs(A[max_index][k])):
            max_index = i

    if max_index != k:
        A[[k, max_index]] = A[[max_index, k]]
        b[[k, max_index]] = b[[max_index, k]]

def forward_elimination(A,b):
    pass

def forward_substitution(A,b):
    pass

def backward_substitution(A,b):
    pass

