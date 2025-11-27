# 0-based index
# rtol: 1e-05
# atol: 1e-08
import numpy as np
from abc import ABC, abstractmethod
from typing_extensions import override

# Base class for linear solvers
class LineraSolver(ABC):
    def __init__(self, A, b, precision=5):
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.n = len(b)
        self.precision = precision
        self.steps = []

    @abstractmethod
    def solve(self):
        pass
    
    def addStep(self, message, data):
        self.steps.append((message, data))
    
    def getSteps(self):
        return self.steps
    
    
# helper functions for direct methods
class DirectSolver(LineraSolver):
    def __init__(self, A, b, precision=5, withScaling=False):
        super().__init__(A, b, precision)
        self.withScaling = withScaling
        self.scalar = None
        
    def scaling(self, A):
        n = A.shape[0]
        self.scalar = np.zeros(n)
        
        for i in range(n):
            largest_coef = max(abs(A[i, :n])) # find the largest coefficient magnitude in row i
            self.scalar[i] = largest_coef
            if np.isclose(largest_coef, 0): # check for any zero row
                raise ValueError("Matrix is singular or near-singular")
    
    def partial_pivoting(self, A, b, k):
        n = A.shape[0]
        max_index = k
        
        if self.withScaling is False:
            # pivoting without scaling
            for i in range(k, n):
                if abs(A[i][k]) > abs(A[max_index][k]):
                    max_index = i
        else:
            # pivoting with scaling
            big = abs(A[k][k]) / self.scalar[k]
            for i in range(k+1, n):
                dummy = abs(A[i][k]) / self.scalar[i]
                if dummy > big:
                    big = dummy
                    max_index = i

        if max_index != k:
            A[[k, max_index]] = A[[max_index, k]]
            b[[k, max_index]] = b[[max_index, k]]
            if self.scalar is not None:
                self.scalar[[k, max_index]] = self.scalar[[max_index, k]]
    
                
    def isSingular(self, pivot, index):
        if self.withScaling is False:
            return np.isclose(pivot, 0)
        else:
            return np.isclose(pivot/self.scalar[index], 0)
    
                
    def forward_elimination(self, A, b):
        n = A.shape[0]
        
        # compute scaling if needed and raise error for singularity
        self.scaling(A) if self.withScaling else None 
        
        for k in range(0, n - 1):  # row traverse(find the row to pivot)
            self.partial_pivoting(A, b, k)

            if self.isSingular(A[k][k], k):  # Check for singularity (pivot is zero)
                raise ValueError(f"Matrix is singular or near-singular at index {k}")
            
            for i in range(k + 1, n):  # row traverse(apply the elimination for specific row)
                factor = A[i][k] / A[k][k]
                A[i, k:] = np.round(A[i, k:] - factor * A[k, k:], decimals=self.precision)
                b[i] = np.round(b[i] - (factor * b[k]), decimals=self.precision)
                self.steps.append((A.copy(), b.copy()))
        
        if self.isSingular(A[n-1][n-1], n-1):  # Check for singularity (last pivot after elimination is zero)
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
                self.steps.append((A.copy(), b.copy()))

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

    
# helper functions for iterative methods    
class IterativeSolver(LineraSolver):
    def __init__(self, A, b, precision=5, initial_guess=None, num_of_ites=None, abs_rel_error=None):
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
        self.steps.clear()
        i = 0
        x_old = self.initial_guess.copy()
        x_new = self.initial_guess.copy()
        
        if self.abs_rel_error is None:
            for i in range(self.num_of_ites):
                x_new = self.iterate(self.A, self.b, x_old)
                x_old = x_new.copy()
            return x_new
        
        elif self.num_of_ites is None:
            # Diagonally Dominant test
            #for i in range(self.n):
            #    sum_row = sum(abs(self.A[i, :self.n]))
            #    if abs(self.A[i][i]) < sum_row - abs(self.A[i][i]):
            #        raise ValueError("The matrix is not diagonally dominant (May not converge)")
            
            self.num_of_ites = 0
            while self.num_of_ites < 50:
                x_new = self.iterate(self.A, self.b, x_old)
                self.num_of_ites += 1
                if self.calculate_error(x_old, x_new) < self.abs_rel_error:
                    return x_new
                x_old = x_new.copy()
                
            if self.num_of_ites == 50:
                raise ValueError("The method did not converge within 50 iterations")

    def calculate_error(self, x_old, x_new):
        return np.max(np.abs(x_new - x_old) / np.maximum(np.abs(x_new), 1e-12)) * 100