# 0-based index
# rtol: 1e-05
# atol: 1e-08
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
    def __init__(self, A, b, precision=5, withScaling=False):
        super().__init__(A, b, precision)
        self.withScaling = withScaling
        
    def scaling(self, A):
        n = A.shape[0]
        scalar = np.zeros(n)
        
        for i in range(n):
            largest_coef = max(abs(A[i, :n])) # find the largest coefficient magnitude in row i
            scalar[i] = largest_coef
            
        return scalar
    
    def partial_pivoting(self, A, b, k, scalar):
        n = A.shape[0]
        max_index = k
        
        if scalar is None: 
            # pivoting without scaling
            for i in range(k, n):
                if abs(A[i][k]) > abs(A[max_index][k]):
                    max_index = i
        else:
            # pivoting with scaling
            big = abs(A[k][k]) / scalar[k]
            for i in range(k+1, n):
                dummy = abs(A[i][k]) / scalar[i]
                if dummy > big:
                    big = dummy
                    max_index = i

        if max_index != k:
            A[[k, max_index]] = A[[max_index, k]]
            b[[k, max_index]] = b[[max_index, k]]
            if scalar is not None:
                scalar[[k, max_index]] = scalar[[max_index, k]]
    
                
    def isSingular(self, pivot, scalarValue=None):
        if scalarValue is None:
            return np.isclose(pivot, 0)
        else:
            return np.isclose(pivot/scalarValue, 0)
    
                
    def forward_elimination(self, A, b):
        n = A.shape[0]
        
        # compute scaling if needed
        scalar = self.scaling(A) if self.withScaling else None
    
        # check for any zero row (true singularity)
        if scalar is not None and np.any(np.isclose(scalar, 0)):
            raise ValueError("Matrix is singular or near-singular")
        
        for k in range(0, n - 1):  # row traverse(find the row to pivot)
            self.partial_pivoting(A, b, k, scalar)

            if self.isSingular(A[k][k], scalar[k] if scalar is not None else None):  # Check for singularity (pivot is zero)
                raise ValueError("Matrix is singular or near-singular")
            
            for i in range(k + 1, n):  # row traverse(apply the elimination for specific row)
                factor = A[i][k] / A[k][k]
                A[i, k:] = np.round(A[i, k:] - factor * A[k, k:], decimals=self.precision)
                b[i] = np.round(b[i] - (factor * b[k]), decimals=self.precision)
        
        if self.isSingular(A[n-1][n-1], scalar[n-1] if scalar is not None else None):  # Check for singularity (last pivot after elimination is zero)
            raise ValueError("Matrix is singular or near-singular")     

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


class DoolittleLUDecomposition(DirectSolver):
    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()

        n = A_bar.shape[0]
        L = np.zeros((n, n))
        
        # compute scaling if needed
        scalar = self.scaling(A_bar) if self.withScaling else None
    
        # check for any zero row (true singularity)
        if scalar is not None and np.any(np.isclose(scalar, 0)):
            raise ValueError("Matrix is singular or near-singular")

        for k in range(0, n - 1):  # row traverse(find the row to pivot)
            self.partial_pivoting(A_bar, b_bar, k, scalar)

            if self.isSingular(A_bar[k][k], scalar[k] if scalar is not None else None):  # Check for singularity (pivot is zero)
                raise ValueError("Matrix is singular or near-singular.")
            
            for i in range(k + 1, n):  # row traverse(apply the elimination for specific row)
                factor = A_bar[i][k] / A_bar[k][k]
                L[i][k] = factor  # to store factors
                A_bar[i, k:] = np.round(A_bar[i, k:] - factor * A_bar[k, k:], decimals=self.precision)
                
        if self.isSingular(A_bar[n-1][n-1], scalar[n-1] if scalar is not None else None):  # Check for singularity (last pivot after elimination is zero)
            raise ValueError("Matrix is singular or near-singular.")
        
        np.fill_diagonal(L, 1)
        U = A_bar

        y = self.forward_substitution(L, b_bar)  # result of the system Ly = b
        solution = self.backward_substitution(U, y)  # result of Ux = y
        return np.round(solution, decimals=self.precision)

class CroutLUDecomposition(DirectSolver):

    @override
    def solve(self):
        A_bar = self.A.copy().T  # use the transpose and apply same Doolittle logic
        b_bar = self.b.copy()

        n = A_bar.shape[0]
        L = np.zeros((n, n))
        o = np.arange(n)   # To track the order of solution

        for k in range(0, n - 1):  # we need custom pivoting method so we don't touch b matrix
            max_index = k
            for i in range(k, n):
                if abs(A_bar[i][k]) > abs(A_bar[max_index][k]):
                    max_index = i
            if max_index != k:
                # Swap rows in A_bar (equivalent to swapping cols in A)
                A_bar[[k, max_index]] = A_bar[[max_index, k]]
                # Swap the order tracker
                o[[k, max_index]] = o[[max_index, k]]

            if np.isclose(A_bar[k][k], 0):  # Check for singularity (pivot is zero)
                raise ValueError("Matrix is singular or near-singular.")
            for i in range(k + 1, n):  # row traverse (apply the elimination for specific row)
                factor = A_bar[i][k] / A_bar[k][k]
                L[i][k] = factor  # to store factors
                A_bar[i, k:] = np.round(A_bar[i, k:] - factor * A_bar[k, k:], decimals=self.precision)
                
        if np.isclose(A_bar[n-1][n-1], 0):  # Check for singularity (last pivot after elimination is zero)
            raise ValueError("Matrix is singular or near-singular.")

        np.fill_diagonal(L, 1)
        U = A_bar

        L_Crout = U.T
        U_Crout = L.T

        y = self.forward_substitution(L_Crout, b_bar) # result of the system Ly = b
        UnOrdered_solution = self.backward_substitution(U_Crout, y)  # result of Ux = y

        Ordered_solution = np.zeros(n)

        for i in range(n):
            Ordered_solution[o[i]] = UnOrdered_solution[i]

        return np.round(Ordered_solution, decimals=self.precision)
    
class CholeskyLUDecomposition(DirectSolver):
    
    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        n = A_bar.shape[0]
        
        if not np.array_equal(A_bar, A_bar.T):  # Check for symmetry
            raise ValueError("Matrix is not symmetric")
        
        for k in range(0, n):
            for i in range(0, k): # calculate the elements below the diagonal
                A_bar[k][i] = np.round((A_bar[k][i] - np.sum(A_bar[i, :i]*A_bar[k, :i])) / A_bar[i][i], decimals=self.precision)
                A_bar[i][k] = A_bar[k][i]
                
            # Compute diagonal elements
            A_bar[k][k] = np.round(np.sqrt(A_bar[k][k] - np.sum(A_bar[k, :k]**2)), decimals=self.precision)
            
            if np.isclose(A_bar[k][k], 0):  # Check for singularity
                raise ValueError("Matrix is singular or near-singular")
            elif np.isnan(A_bar[k][k]) or np.iscomplexobj(A_bar[k][k]): # Check for positive definiteness
                raise ValueError("Matrix is not positive definite")
            
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