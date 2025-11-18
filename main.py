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


class LUDecomposition(DirectSolver):
    pass


class IterativeSolver(LineraSolver):
    def getParameters(self, initial_guess, num_of_ites, abs_rel_erroe):
        self.initial_guess = initial_guess
        self.num_of_ites = num_of_ites
        self.abs_rel_erroe = abs_rel_erroe

    @abstractmethod
    def iterate(self, A, b, x):
        pass

    def solve(self):
        pass

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



