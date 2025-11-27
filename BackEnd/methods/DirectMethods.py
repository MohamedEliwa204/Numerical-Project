from .BaseFunctions import *

class GaussElimination(DirectSolver):
    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        self.steps.clear()

        self.forward_elimination(A_bar, b_bar)
        solution = self.backward_substitution(A_bar, b_bar)
        return np.round(solution, decimals=self.precision)


class GaussJordan(DirectSolver):
    @override
    def solve(self):
        self.steps.clear()
        A_bar = self.A.copy()
        b_bar = self.b.copy()

        self.forward_elimination(A_bar, b_bar)
        self.backward_elimination(A_bar, b_bar)
        solution = b_bar

        return np.round(solution, decimals=self.precision)


class DoolittleLUDecomposition(DirectSolver):
    @override
    def solve(self):
        self.steps.clear()
        A_bar = self.A.copy()
        b_bar = self.b.copy()

        n = A_bar.shape[0]
        L = np.zeros((n, n))
        
        # compute scaling if needed and raise error for singularity
        self.scaling(A_bar) if self.withScaling else None

        for k in range(0, n - 1):  # row traverse(find the row to pivot) and pivoting
            old_row = k
            max_index = k
            if self.withScaling is False:
                for i in range(k, n):
                    if abs(A_bar[i][k]) > abs(A_bar[max_index][k]):
                        max_index = i
            else:
                big = abs(A_bar[k][k]) / self.scalar[k]
                for i in range(k + 1, n):
                    dummy = abs(A_bar[i][k]) / self.scalar[i]
                    if dummy > big:
                        big = dummy
                        max_index = i

            if max_index != k:
                A_bar[[k, max_index]] = A_bar[[max_index, k]]
                b_bar[[k, max_index]] = b_bar[[max_index, k]]
                if self.scalar is not None:
                    self.scalar[[k, max_index]] = self.scalar[[max_index, k]]
                if k > 0:
                    L[[k, max_index], :k] = L[[max_index, k], :k] # swap factors in L too

            if self.isSingular(A_bar[k][k], k):  # Check for singularity (pivot is zero)
                raise ValueError("Matrix is singular or near-singular.")
            
            for i in range(k + 1, n):  # row traverse(apply the elimination for specific row)
                factor = self.round_significant(A_bar[i][k] / A_bar[k][k])
                L[i][k] = factor  # to store factors
                tempRow = self.round_significant(factor * A_bar[k, k:])
                A_bar[i, k:] = self.round_significant(A_bar[i, k:] - tempRow)
                
        if self.isSingular(A_bar[n-1][n-1], n-1):  # Check for singularity (last pivot after elimination is zero)
            raise ValueError("Matrix is singular or near-singular.")
        
        np.fill_diagonal(L, 1)
        U = A_bar

        y = self.forward_substitution(L, b_bar)  # result of the system Ly = b
        solution = self.backward_substitution(U, y)  # result of Ux = y
        return solution


class CroutLUDecomposition(DirectSolver):
    @override
    def solve(self):
        self.steps.clear()
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
                # Swap the order tracker (to keep order of the right solutions)
                o[[k, max_index]] = o[[max_index, k]]
                # swap rows in L (factors)
                L[[k, max_index]] = L[[max_index, k]]

            if np.isclose(A_bar[k][k], 0):  # Check for singularity (pivot is zero)
                raise ValueError("Matrix is singular or near-singular.")
            for i in range(k + 1, n):  # row traverse (apply the elimination for specific row)
                factor = self.round_significant(A_bar[i][k] / A_bar[k][k])
                L[i][k] = factor  # to store factors
                tempRow = self.round_significant(factor * A_bar[k, k:])
                A_bar[i, k:] = self.round_significant(A_bar[i, k:] - tempRow)
                
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

        return Ordered_solution

   
class CholeskyLUDecomposition(DirectSolver): 
    @override
    def solve(self):
        self.steps.clear()
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        n = A_bar.shape[0]
        
        if not np.array_equal(A_bar, A_bar.T):  # Check for symmetry
            raise ValueError("Matrix is not symmetric")
        
        for k in range(0, n):
            for i in range(0, k): # calculate the elements below the diagonal
                sum = np.sum(self.round_significant(A_bar[k, :i] * A_bar[i, :i]))
                A_bar[k][i] = self.round_significant(self.round_significant(A_bar[k][i] - sum) / A_bar[i][i])
                A_bar[i][k] = A_bar[k][i]
                
            # Compute diagonal elements
            sum = np.sum(self.round_significant(A_bar[k, :k]**2))
            A_bar[k][k] = self.round_significant(np.sqrt(self.round_significant(A_bar[k][k] - sum)))
            
            if np.isclose(A_bar[k][k], 0):  # Check for singularity
                raise ValueError("Matrix is singular or near-singular")
            elif np.isnan(A_bar[k][k]) or np.iscomplexobj(A_bar[k][k]): # Check for positive definiteness
                raise ValueError("Matrix is not positive definite")
            
        y = self.forward_substitution(np.tril(A_bar), b_bar)
        x = self.backward_substitution(np.triu(A_bar), y)
        return x