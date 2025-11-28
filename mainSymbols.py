import sympy as sp
from abc import ABC, abstractmethod
from typing_extensions import override


class SymLinearSolver(ABC):
    def __init__(self, n, A, b):  # n: number of rows, A: 2D list of strings, b: 1D list of strings
        # Parse each cell of A and b as a SymPy expression
        # This allows actual values like "2", "3.5" or symbols like "a", "2*x + y"
        self.A = sp.Matrix(n, n, lambda i, j: sp.sympify(A[i][j]))
        self.b = sp.Matrix(n, 1, lambda i, j: sp.sympify(b[i]))
        self.steps = []
        self.describitive_steps = []
        self.Xs_steps = []
        self.Ys_steps = []
        self.n = n

    @abstractmethod
    def solve(self):
        pass


class SymDirectSolver(SymLinearSolver):
    def __init__(self, n, A, b):
        super().__init__(n, A, b)

    def forward_elimination(self, A: sp.Matrix, b: sp.Matrix):
        aug = A.row_join(b)
        for i in range(self.n):
            pivot = aug[i, i]

            if pivot == 0:
                continue

            for r in range(i + 1, self.n):
                factor = aug[r, i] / pivot
                self.describitive_steps.append(
                    f"R{r + 1} ← R{r + 1} - ({factor}) * R{i + 1}"
                )
                aug[r, :] = aug[r, :] - factor * aug[i, :]
                # Append (A_part, b_part) tuple like DirectSolver does
                A_step = aug[:, :self.n].copy()
                b_step = aug[:, self.n:].copy()
                self.steps.append((A_step, b_step))

        return aug

    def backward_elimination(self, A: sp.Matrix, b: sp.Matrix):
        aug = A.row_join(b)

        for i in reversed(range(self.n)):
            pivot = aug[i, i]

            if pivot == 0:
                continue

            for r in range(i - 1, -1, -1):  # rows above the pivot
                factor = aug[r, i] / pivot
                self.describitive_steps.append(
                    f"R{r + 1} ← R{r + 1} - ({factor}) * R{i + 1}"
                )
                aug[r, :] = aug[r, :] - factor * aug[i, :]
                # Append (A_part, b_part) tuple like DirectSolver does
                A_step = aug[:, :self.n].copy()
                b_step = aug[:, self.n:].copy()
                self.steps.append((A_step, b_step))
        return aug

    def forward_substitution(self, L: sp.Matrix, b: sp.Matrix):
        n = L.rows
        x = sp.Matrix(sp.symbols(f"x0:{n}"))

        x[0] = b[0] / L[0, 0]
        self.Ys_steps.append(f"Y1 = {sp.simplify(x[0])}")
        for i in range(1, n):
            sum_ = 0
            for j in range(i):
                sum_ += L[i, j] * x[j]

            x[i] = (b[i] - sum_) / L[i, i]
            self.Ys_steps.append(f"Y{i + 1} = {sp.simplify(x[i])}")

        return x

    def backward_substitution(self, U: sp.Matrix, b: sp.Matrix):
        n = U.rows
        x = sp.Matrix(sp.symbols(f"x1:{n + 1}"))
        x[n - 1] = b[n - 1] / U[n - 1, n - 1]
        self.Xs_steps.append(f"X{n} = ({sp.simplify(x[n - 1])})")

        for i in range(n - 2, -1, -1):  # traverse rows backward
            sum_ = 0
            for j in range(i + 1, n):  # traverse columns forward
                sum_ += U[i, j] * x[j]

            x[i] = (b[i] - sum_) / U[i, i]
            self.Xs_steps.append(f"X{i + 1} = {sp.simplify(x[i])}")

        return x


class SymGaussElimination(SymDirectSolver):
    def __init__(self, n, A, b):
        super().__init__(n, A, b)

    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        aug = self.forward_elimination(A_bar, b_bar)
        U = aug[:, :self.n]  # first n columns
        b_new = aug[:, self.n:]  # last column
        solution = self.backward_substitution(U, b_new)
        return sp.simplify(solution)


class SymGaussJordan(SymDirectSolver):
    def __init__(self, n, A, b):
        super().__init__(n, A, b)

    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        aug = self.forward_elimination(A_bar, b_bar)
        U = aug[:, :self.n]
        b_new = aug[:, self.n:]
        aug = self.backward_elimination(U, b_new)
        solution = aug[:, self.n:]
        return sp.simplify(solution)


class SymDoolittleLUDecomposition(SymDirectSolver):
    def __init__(self, n, A, b):
        super().__init__(n, A, b)

    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        n = self.n
        L = sp.zeros(n, n)

        # Perform LU factorization
        for k in range(n - 1):
            if A_bar[k, k] == 0:
                continue

            for i in range(k + 1, n):
                factor = A_bar[i, k] / A_bar[k, k]
                L[i, k] = factor
                A_bar[i, k:] = A_bar[i, k:] - factor * A_bar[k, k:]
                # Append (L, U) tuple like DirectMethods does
                L_step = L.copy()
                for d in range(n):
                    L_step[d, d] = 1  # Fill diagonal with 1s
                self.steps.append((L_step, A_bar.copy()))

        for i in range(n):
            L[i, i] = 1

        U = A_bar

        y = self.forward_substitution(L, b_bar)
        solution = self.backward_substitution(U, y)

        return sp.simplify(solution)


class SymCroutLUDecomposition(SymDirectSolver):
    def __init__(self, n, A, b):
        super().__init__(n, A, b)

    @override
    def solve(self):
        A_bar = self.A.copy().T  # Transpose for Crout method
        b_bar = self.b.copy()
        n = self.n
        L = sp.zeros(n, n)

        # Perform LU factorization on transposed matrix
        for k in range(n - 1):
            if A_bar[k, k] == 0:
                continue

            for i in range(k + 1, n):
                factor = A_bar[i, k] / A_bar[k, k]
                L[i, k] = factor
                A_bar[i, k:] = A_bar[i, k:] - factor * A_bar[k, k:]
                # Append (L_Crout, U_Crout) tuple like DirectMethods does
                # L.T becomes U_Crout, so we need 1s on L's diagonal for U to have 1s on diagonal
                L_step = L.copy()
                for d in range(n):
                    L_step[d, d] = 1
                self.steps.append((A_bar.T.copy(), L_step.T))

        for i in range(n):
            L[i, i] = 1

        # For Crout: transpose back to get proper L and U
        L_Crout = A_bar.T
        U_Crout = L.T

        y = self.forward_substitution(L_Crout, b_bar)
        solution = self.backward_substitution(U_Crout, y)

        return sp.simplify(solution)


class SymCholeskyLUDecomposition(SymDirectSolver):
    def __init__(self, n, A, b):
        super().__init__(n, A, b)

    @override
    def solve(self):
        A_bar = self.A.copy()
        b_bar = self.b.copy()
        n = self.n

        # Check if matrix is symmetric
        if A_bar != A_bar.T:
            raise ValueError("Matrix is not symmetric - Cholesky decomposition requires a symmetric matrix")

        # Initialize L and U for step tracking
        L = sp.zeros(n, n)
        U = sp.zeros(n, n)

        # Compute Cholesky decomposition: A = L * L^T
        for k in range(n):
            # Calculate elements below the diagonal
            for i in range(k):
                sum_term = sum(A_bar[i, j] * A_bar[k, j] for j in range(i))
                A_bar[k, i] = (A_bar[k, i] - sum_term) / A_bar[i, i]
                A_bar[i, k] = A_bar[k, i]
                # Update L and U for this step
                L[k, i] = A_bar[k, i]
                U[i, k] = A_bar[i, k]
                self.steps.append((L.copy(), U.copy()))

            # Compute diagonal element
            sum_sq = sum(A_bar[k, j]**2 for j in range(k))
            A_bar[k, k] = sp.sqrt(A_bar[k, k] - sum_sq)
            # Update L and U diagonal
            L[k, k] = A_bar[k, k]
            U[k, k] = A_bar[k, k]
            self.steps.append((L.copy(), U.copy()))

        y = self.forward_substitution(L, b_bar)
        solution = self.backward_substitution(L.T, y)

        return sp.simplify(solution)


