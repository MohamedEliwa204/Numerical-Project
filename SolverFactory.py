from abc import ABC, abstractmethod
from main import (
    GaussElimination,
    GaussJordan,
    DoolittleLUDecomposition,
    CroutLUDecomposition,
    CholeskyLUDecomposition,
    GaussSeidel,
    JacobiIteration
)
from mainSymbols import (
    SymGaussElimination,
    SymGaussJordan,
    SymDoolittleLUDecomposition,
    SymCroutLUDecomposition,
    SymCholeskyLUDecomposition,
)


class AbstractSolverFactory(ABC):

    @abstractmethod
    def create_gauss_elimination(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_gauss_jordan(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_doolittle_lu(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_crout_lu(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_cholesky(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_gauss_seidel(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_jacobi(self, *args, **kwargs):
        pass

    @abstractmethod
    def create_solver(self, method_name, *args, **kwargs):
        pass

    @abstractmethod
    def get_available_methods(self):
        pass


class NumericalSolverFactory(AbstractSolverFactory):

    def create_gauss_elimination(self, A, b, precision=5, withScaling=False):
        return GaussElimination(A, b, precision=precision, withScaling=withScaling)

    def create_gauss_jordan(self, A, b, precision=5, withScaling=False):
        return GaussJordan(A, b, precision=precision, withScaling=withScaling)

    def create_doolittle_lu(self, A, b, precision=5, withScaling=False):
        return DoolittleLUDecomposition(A, b, precision=precision, withScaling=withScaling)

    def create_crout_lu(self, A, b, precision=5, withScaling=False):
        return CroutLUDecomposition(A, b, precision=precision, withScaling=withScaling)

    def create_cholesky(self, A, b, precision=5, withScaling=False):
        return CholeskyLUDecomposition(A, b, precision=precision, withScaling=withScaling)

    def create_gauss_seidel(self, A, b, precision=5, initial_guess=None, num_of_ites=None, abs_rel_error=None):
        return GaussSeidel(A, b, precision=precision, initial_guess=initial_guess,
                          num_of_ites=num_of_ites, abs_rel_error=abs_rel_error)

    def create_jacobi(self, A, b, precision=5, initial_guess=None, num_of_ites=None, abs_rel_error=None):
        return JacobiIteration(A, b, precision=precision, initial_guess=initial_guess,
                              num_of_ites=num_of_ites, abs_rel_error=abs_rel_error)

    def create_solver(self, method_name, A, b, **kwargs):
        method_name = method_name.lower().replace(' ', '_')

        method_map = {
            'gauss_elimination': self.create_gauss_elimination,
            'gauss_jordan': self.create_gauss_jordan,
            'doolittle_lu': self.create_doolittle_lu,
            'crout_lu': self.create_crout_lu,
            'cholesky': self.create_cholesky,
            'gauss_seidel': self.create_gauss_seidel,
            'jacobi': self.create_jacobi,
        }

        if method_name in method_map:
            return method_map[method_name](A, b, **kwargs)
        else:
            raise ValueError(f"Unknown method '{method_name}'. Available methods: {', '.join(method_map.keys())}")

    def get_available_methods(self):
        return {
            'direct': ['gauss_elimination', 'gauss_jordan', 'doolittle_lu', 'crout_lu', 'cholesky'],
            'iterative': ['gauss_seidel', 'jacobi']
        }


class SymbolicSolverFactory(AbstractSolverFactory):

    def create_gauss_elimination(self, n):
        return SymGaussElimination(n)

    def create_gauss_jordan(self, n):
        return SymGaussJordan(n)

    def create_doolittle_lu(self, n):
        return SymDoolittleLUDecomposition(n)

    def create_crout_lu(self, n):
        return SymCroutLUDecomposition(n)

    def create_cholesky(self, n):
        return SymCholeskyLUDecomposition(n)

    def create_gauss_seidel(self, n):
        raise NotImplementedError("Symbolic iterative methods not yet implemented")

    def create_jacobi(self, n):
        raise NotImplementedError("Symbolic iterative methods not yet implemented")

    def create_solver(self, method_name, n):
        method_name = method_name.lower().replace(' ', '_')

        method_map = {
            'gauss_elimination': self.create_gauss_elimination,
            'gauss_jordan': self.create_gauss_jordan,
            'doolittle_lu': self.create_doolittle_lu,
            'crout_lu': self.create_crout_lu,
            'cholesky': self.create_cholesky,
            'gauss_seidel': self.create_gauss_seidel,
            'jacobi': self.create_jacobi,
        }

        if method_name in method_map:
            return method_map[method_name](n)
        else:
            raise ValueError(f"Unknown method '{method_name}'. Available methods: {', '.join(method_map.keys())}")

    def get_available_methods(self):
        return {
            'direct': ['gauss_elimination', 'gauss_jordan', 'doolittle_lu', 'crout_lu', 'cholesky'],
            'iterative': ['gauss_seidel', 'jacobi']
        }


if __name__ == "__main__":
    print("=== Numerical Solver Factory ===")
    num_factory = NumericalSolverFactory()
    A = [[4, -1, 0], [-1, 4, -1], [0, -1, 4]]
    b = [15, 10, 10]
    solver = num_factory.create_solver('gauss_elimination', A, b, precision=5)
    print(f"Solution: {solver.solve()}")

    print("\n=== Symbolic Solver Factory ===")
    sym_factory = SymbolicSolverFactory()
    sym_solver = sym_factory.create_solver('gauss_elimination', n=3)
    print(f"Solution:\n{sym_solver.solve()}")

    print("\n=== Available Methods ===")
    print("Numerical:", num_factory.get_available_methods())
    print("Symbolic:", sym_factory.get_available_methods())

