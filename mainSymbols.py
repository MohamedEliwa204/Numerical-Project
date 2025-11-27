import sympy as sp
from abc import ABC, abstractmethod
from typing_extensions import override


class SymLinearSolver(ABC):
    def __init__(self, n):  # here n tthe number of roows in matrix instead of A
        self.A = sp.Matrix(n, n, lambda i, j: sp.symbols(f"a{i + 1}{j + 1}"))
        self.b = sp.Matrix(n, 1, lambda i, j: sp.symbols(f"b{i + 1}"))
        self.steps = []
        self.n = n

    @abstractmethod
    def solve(self):
        pass


class SymDirectSolver(SymLinearSolver):
    def __init__(self, n):
        super().__init__(n)

    def forward_elimination(self, A: sp.Matrix, b: sp.Matrix):
        aug = A.row_join(b);
        for i in range(self.n):
            pivot = aug[i][i]

            if pivot == 0:
                continue

            for r in range(i+1, self.n):
                factor = aug[r, i] / pivot
                self.steps.append(
                    f"R{r+1} ← R{r+1} - ({factor}) * R{i+1}"
                )
                aug[r, :] = aug[r, :] - factor * aug[i, :]
                self.steps.append(str(aug))


        return aug

    def forward_substitution(self, L:sp.Matrix, b:sp.Matrix):
        pass





