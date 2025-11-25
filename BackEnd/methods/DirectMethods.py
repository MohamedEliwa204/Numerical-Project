from .BaseFunctions import *

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
        
        # compute scaling if needed and raise error for singularity
        self.scaling(A_bar) if self.withScaling else None

        for k in range(0, n - 1):  # row traverse(find the row to pivot)
            self.partial_pivoting(A_bar, b_bar, k)

            if self.isSingular(A_bar[k][k], k):  # Check for singularity (pivot is zero)
                raise ValueError("Matrix is singular or near-singular.")
            
            for i in range(k + 1, n):  # row traverse(apply the elimination for specific row)
                factor = A_bar[i][k] / A_bar[k][k]
                L[i][k] = factor  # to store factors
                A_bar[i, k:] = np.round(A_bar[i, k:] - factor * A_bar[k, k:], decimals=self.precision)
                
        if self.isSingular(A_bar[n-1][n-1], n-1):  # Check for singularity (last pivot after elimination is zero)
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