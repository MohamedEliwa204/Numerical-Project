# 0-based index
import numpy as np
from abc import ABC, abstractmethod

from typing_extensions import override


class LineraSolver(ABC):
    def __init__(self, A, b, precision=5):
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.n = len(b)
        self.precision = precision

    @abstractmethod
    def solve(self):
        pass


class DirectSolver(LineraSolver):
    def partial_pivoting(self, A, b, k):
        n = A.shape[0]
        max_index = k
        for i in range(k, n):
            if abs(A[i][k]) > abs(A[max_index][k]):
                max_index = i

        if max_index != k:
            A[[k, max_index]] = A[[max_index, k]]
            b[[k, max_index]] = b[[max_index, k]]

    def forward_elimination(self, A, b):
        n = A.shape[0]
        for k in range(0, n - 1):  # row traverse(find the row to pivot)
            self.partial_pivoting(A, b, k)

            if np.isclose(A[k][k], 0):  # Check for singularity
                raise ValueError("Matrix is singular or near-singular.")
            for i in range(k + 1, n):  # row traverse(apply the elimination for specific row)
                factor = A[i][k] / A[k][k]
                A[i, k:] = np.round(A[i, k:] - factor * A[k, k:], decimals=self.precision)
                b[i] = np.round(b[i] - (factor * b[k]), decimals=self.precision)

    def backward_elimination(self, A, b):
        n = A.shape[0]

        for k in range(n - 1, -1, -1):
            pivot = A[k][k]
            A[k] = A[k] / pivot
            b[k] = b[k] / pivot
            for i in range(0, k):
                factor = A[i][k]
                A[i] = A[i] - factor * A[k]
                b[i] = b[i] - factor * b[k]

    def forward_substitution(self, L, b):
        n = L.shape[0]
        x = np.zeros(n)
        x[0] = b[0] / L[0][0]
        for i in range(1, n):  # row traverse forward
            sum = 0
            for j in range(0, i):  # column traverse backward
                sum = sum + (x[j] * L[i][j])

            x[i] = (b[i] - sum) / L[i][i]

        return x

    def backward_substitution(self, A, b):
        n = A.shape[0]
        x = np.zeros(n)
        x[n - 1] = b[n - 1] / A[n - 1][n - 1]
        for i in range(n - 2, -1, -1):  # row traverse backward
            sum = 0
            for j in range(i + 1, n):  # column traverse forward
                sum = sum + (x[j] * A[i][j])

            x[i] = (b[i] - sum) / A[i][i]

        return x


class GaussElimination(DirectSolver):

    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()

        self.forward_elimination(A_bar, b_bar)
        solution = self.backward_substitution(A_bar, b_bar)
        return np.round(solution, decimals=self.precision)


class GaussJordan(DirectSolver):
    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()

        self.forward_elimination(A_bar, b_bar)
        self.backward_elimination(A_bar, b_bar)
        solution = b_bar

        return np.round(solution, decimals=self.precision)


class CholeskyLUDecomposition(DirectSolver):
    
    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        n = A_bar.shape[0]
        
        for k in range(0, n):
            for i in range(0, k): # calculate the elements below the diagonal
                A_bar[k][i] = np.round((A_bar[k][i] - np.sum(A_bar[i, :i]*A_bar[k, :i])) / A_bar[i][i], decimals=self.precision)
                A_bar[i][k] = A_bar[k][i]
                
            # Compute diagonal element
            A_bar[k][k] = np.round(np.sqrt(A_bar[k][k] - np.sum(A_bar[k, :k]**2)), decimals=self.precision)
            
            if np.isclose(A_bar[k][k], 0):  # Check for singularity
                raise ValueError("Matrix is singular or near-singular.")
            
        y = self.forward_substitution(np.tril(A_bar), b_bar)
        x = self.backward_substitution(np.triu(A_bar), y)
        return np.round(x, decimals=self.precision)
        

class IterativeSolver(LineraSolver):
    def __init__(self, A, b, precision=5, initial_guess=None, num_of_ites=50, abs_rel_error=0.0001):
        super().__init__(A, b, precision)


        self.num_of_ites = num_of_ites
        self.abs_rel_error = abs_rel_error

        if initial_guess is None:
            self.initial_guess = np.zeros(self.n)
        else:
            self.initial_guess = np.array(initial_guess, dtype=float)

    @abstractmethod
    def iterate(self, A, b, x):
        pass

    @override
    def solve(self):
        i = 0
        x_old = self.initial_guess.copy()
        x_new = self.initial_guess.copy()
        for i in range(self.num_of_ites):
            x_new = self.iterate(self.A, self.b, x_old)
            if self.calculate_error(x_old, x_new) < self.abs_rel_error:
                return x_new
            x_old = x_new.copy()
        return x_new

    def calculate_error(self, x_old, x_new):
        return np.max(np.abs(x_new - x_old) / np.maximum(np.abs(x_new), 1e-12)) * 100


class GaussSeidel(IterativeSolver):
    @override
    def iterate(self, A, b, x):
        x_old = x.copy()
        x_new = x.copy()

        for k in range(0, self.n):
            x_new[k] = (b[k] - (np.dot(A[k, :k], x_new[:k])) - np.dot(A[k, k + 1:], x_old[k + 1:])) / A[k][k]

        return x_new


class JacobiIteration(IterativeSolver):
    @override
    def iterate(self, A, b, x):
        x_old = x.copy()
        x_new = np.zeros_like(x)

        for k in range(0, self.n):
            x_new[k] = (b[k] - (np.dot(A[k, :k], x_old[:k])) - np.dot(A[k, k + 1:], x_old[k + 1:])) / A[k][k]

        return x_new
    
    
A = np.array([
    [25, 15, -5, 10, 5],
    [15, 18,  0,  6, 2],
    [-5,  0, 11,  2, 1],
    [10,  6,  2, 18, 3],
    [5,   2,  1,  3, 10]], dtype=float)

b = np.array([30, 25, 10, 20, 15], dtype=float)

solver = CholeskyLUDecomposition(A, b)
x = solver.solve()
print(x)

L = np.linalg.cholesky(A)
y = np.linalg.solve(L, b)
x = np.linalg.solve(L.T, y)

print(x)