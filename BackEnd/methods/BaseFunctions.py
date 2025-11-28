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
        self.describitive_steps = []
        self.Xs_steps = []
        self.Ys_steps = []
        self.message = ""

    def round_significant(self, value):
        x = np.array(value, dtype=float)

        if np.isscalar(x):
            if not np.isfinite(x):
                return x
            if x == 0:
                return 0
            else:
                digits = self.precision - int(np.floor(np.log10(abs(x)))) - 1
                return round(x, digits)
        else:
            rounded_array = np.zeros_like(x)
            for index, val in np.ndenumerate(x):
                if not np.isfinite(val):
                    rounded_array[index] = val
                elif val == 0:
                    rounded_array[index] = 0
                else:
                    digits = self.precision - int(np.floor(np.log10(abs(val)))) - 1
                    rounded_array[index] = round(val, digits)
            return rounded_array

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
            largest_coef = self.round_significant(max(abs(A[i, :n])))  # apply precision
            self.scalar[i] = largest_coef
            if np.isclose(largest_coef, 0):  # check for any zero row
                raise ValueError("Matrix is singular or near-singular")
    
    def partial_pivoting(self, A, b, k):
        n = A.shape[0]
        max_index = k
        
        if self.withScaling is False:
            # pivoting without scaling
            max_val = self.round_significant(abs(A[k][k]))
            for i in range(k, n):
                current_val = self.round_significant(abs(A[i][k]))
                if current_val > max_val:
                    max_val = current_val
                    max_index = i
        else:
            # pivoting with scaling
            big = self.round_significant(abs(A[k][k]) / self.scalar[k])
            for i in range(k + 1, n):
                dummy = self.round_significant(abs(A[i][k]) / self.scalar[i])
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
                factor = self.round_significant(A[i][k] / A[k][k])

                tempRow = self.round_significant(factor * A[k, k:])
                A[i, k:] = self.round_significant(A[i, k:] - tempRow)

                temp = self.round_significant(factor * b[k])
                b[i] = self.round_significant(b[i] - temp)
                self.describitive_steps.append(
                    f"R{i + 1} ← R{i + 1} - ({np.round(factor, decimals=self.precision)}) * R{k + 1}"
                )

                self.steps.append((A.copy(), b.copy()))
        
        if self.isSingular(A[n-1][n-1], n-1):  # Check for singularity (last pivot after elimination is zero)
            raise ValueError("Matrix is singular or near-singular") 

    def backward_elimination(self, A, b):
        n = A.shape[0]

        for k in range(n - 1, -1, -1):
            pivot = A[k][k]
            A[k] = self.round_significant(A[k] / pivot)
            b[k] = self.round_significant(b[k] / pivot)
            self.steps.append((A.copy(), b.copy()))
            self.describitive_steps.append(
                f"R{k} ← R{k} / {pivot}"
            )
            for i in range(0, k):
                factor = A[i][k]
                
                tempRow = self.round_significant(factor * A[k])
                A[i] = self.round_significant(A[i] - tempRow)

                temp = self.round_significant(factor * b[k])
                b[i] = self.round_significant(b[i] - temp)
                self.describitive_steps.append(
                    f"R{i + 1} ← R{i + 1} - ({np.round(factor, decimals=self.precision)}) * R{k + 1}"
                )
                self.steps.append((A.copy(), b.copy()))

    def forward_substitution(self, L, b):
        n = L.shape[0]
        x = np.zeros(n)
        x[0] = self.round_significant(b[0] / L[0][0])
        self.Ys_steps.append(f"Y1 = ({np.round(b[0], decimals=self.precision)}) / {np.round(L[0][0], decimals=self.precision)} = {np.round(x[0], decimals=self.precision)}")
        for i in range(1, n):  # row traverse forward
            sum = 0
            temp_terms = [f"{np.round(b[i], decimals=self.precision)}"]
            for j in range(0, i):  # column traverse backward
                temp_terms.append(f"(({np.round(x[j], decimals=self.precision)}) * ({np.round(L[i][j], decimals=self.precision)}))")
                sum = self.round_significant(sum + self.round_significant(x[j] * L[i][j]))

            x[i] = self.round_significant(self.round_significant(b[i] - sum) / L[i][i])
            self.Ys_steps.append(f"Y{i + 1} = ({" - ".join(temp_terms)}) / {np.round(L[i][i], decimals=self.precision)} = {np.round(x[i], decimals=self.precision)}")

        return x

    def backward_substitution(self, A, b):
        n = A.shape[0]
        x = np.zeros(n)
        x[n - 1] = self.round_significant(b[n - 1] / A[n - 1][n - 1])
        self.Xs_steps.append(f"X{n} = ({np.round(b[n - 1], decimals=self.precision)}) / {np.round(A[n - 1][n - 1], decimals=self.precision)} = {np.round(x[n - 1], decimals=self.precision)}")
        for i in range(n - 2, -1, -1):  # row traverse backward
            sum = 0
            temp_terms = [f"({np.round(b[i], decimals=self.precision)})"]
            for j in range(i + 1, n):  # column traverse forward
                temp_terms.append(f"(({np.round(x[j], decimals=self.precision)}) * ({np.round(A[i][j], decimals=self.precision)}))")
                sum = self.round_significant(sum + self.round_significant(x[j] * A[i][j]))

            x[i] = self.round_significant(self.round_significant(b[i] - sum) / A[i][i])
            self.Xs_steps.append(f"X{i + 1} = ({" - ".join(temp_terms)}) / {np.round(A[i][i], decimals=self.precision)} = {np.round(x[i], decimals=self.precision)}")

        return x

    
# helper functions for iterative methods    
class IterativeSolver(LineraSolver):
    def __init__(self, A, b, precision=5, initial_guess=None, num_of_ites=None, abs_rel_error=None):
        super().__init__(A, b, precision)

        self.isDiagDominant = True
        self.DiagEleStrictlyGreater = False
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
        self.describitive_steps.clear()
        x_old = self.initial_guess.copy()
        x_new = self.initial_guess.copy()

        # Check for zero diagonal elements
        if np.any(np.isclose(np.diag(self.A), 0)):
             raise ValueError("Matrix has zero diagonal elements. Iterative methods require non-zero diagonal elements.")
        
        # Diagonally Dominant test
        for i in range(self.n):
            sum_row = sum(abs(self.A[i, :self.n]))
            if abs(self.A[i][i]) < sum_row - abs(self.A[i][i]):
                self.isDiagDominant = False
                break
            if abs(self.A[i][i] > sum_row) - abs(self.A[i][i]):
                self.DiagEleStrictlyGreater = True
        if (self.DiagEleStrictlyGreater == False):
            self.isDiagDominant = False
        
        iterations_num = self.num_of_ites
        self.num_of_ites = 0
        
        while self.num_of_ites < iterations_num:
            x_new = self.iterate(self.A, self.b, x_old)
            self.num_of_ites += 1
            if self.calculate_error(x_old, x_new) < self.abs_rel_error:
                return x_new
            x_old = x_new.copy()
                
        if self.num_of_ites == iterations_num:
            if (self.isDiagDominant == False):
                self.message = f"The method could not reach the tolerance required within {iterations_num} iterations (Wouldn't probably converge) ❌"
            else:
                self.message = f"The method could not reach the tolerance required within {iterations_num} iterations although it would converge (Diagonally Dominant) ✅"
            
            return x_new

    def calculate_error(self, x_old, x_new):
        return np.max(np.abs(x_new - x_old) / np.maximum(np.abs(x_new), 1e-12)) * 100
    
    def calculate_individual_error(self, x_old : float, x_new : float):
        return (np.abs(x_new - x_old) / max(np.abs(x_new), 1e-12)) * 100