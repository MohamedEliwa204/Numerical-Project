import sympy as sp
from abc import ABC, abstractmethod
from typing_extensions import override


class SymLinearSolver(ABC):
    def __init__(self, n):  # here n tthe number of roows in matrix instead of A
        self.A = sp.Matrix(n, n, lambda i, j: sp.symbols(f"a{i + 1}{j + 1}"))
        self.b = sp.Matrix(n, 1, lambda i, j: sp.symbols(f"b{i + 1}"))
        self.steps = []
        self.describitive_steps = []
        self.n = n

    @abstractmethod
    def solve(self):
        pass


class SymDirectSolver(SymLinearSolver):
    def __init__(self, n):
        super().__init__(n)

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
                self.steps.append(aug)

        return aug

    def forward_substitution(self, L: sp.Matrix, b: sp.Matrix):
        n = L.rows
        x = sp.Matrix(sp.symbols(f"x0:{n}"))

        x[0] = b[0] / L[0, 0]
        self.steps.append(f"x0 = {b[0]} / {L[0, 0]} = {x[0]}")
        for i in range(1, n):
            sum_ = 0
            for j in range(i):
                sum_ += L[i, j] * x[j]

            x[i] = (b[i] - sum_) / L[i, i]
            self.steps.append(f"x{i} = ({b[i]} - {sum_}) / {L[i, i]} = {x[i]}")

        return x

    def backward_substitution(self, U: sp.Matrix, b: sp.Matrix):
        n = U.rows
        x = sp.Matrix(sp.symbols(f"x1:{n + 1}"))
        x[n - 1] = b[n - 1] / U[n - 1, n - 1]
        self.steps.append(f"x{n - 1} = {x[n - 1]}")

        for i in range(n - 2, -1, -1):  # traverse rows backward
            sum_ = 0
            for j in range(i + 1, n):  # traverse columns forward
                sum_ += U[i, j] * x[j]

            x[i] = (b[i] - sum_) / U[i, i]
            self.steps.append(f"x{i} = ({b[i]} - {sum_}) / {U[i, i]} = {x[i]}")

        return x


class SymGaussElimination(SymDirectSolver):
    @override
    def solve(self):
        pass


class SymGaussJordan(SymDirectSolver):
    @override
    def solve(self):
        pass


class SymIterativeSolver(SymLinearSolver):
    @abstractmethod
    def iterate(self):
        pass

    @override
    def solve(self):
        pass


class SymGaussSeidel(SymIterativeSolver):
    @override
    def iterate(self):
        pass


class SymJacobiIteration(SymIterativeSolver):
    @override
    def iterate(self):
        pass

