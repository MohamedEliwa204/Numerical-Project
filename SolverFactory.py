from abc import ABC, abstractmethod
from BackEnd.linearMethods import (
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
from BackEnd.nonlinearMethods import (
    Bisection,
    FalsePosition,
    FixedPoint,
    OriginalNewtonRaphson,
    ModifiedNewtonRaphson,
    SecantMethod
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

    def create_solver(self, method_name, *args, **kwargs):
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
            return method_map[method_name](*args, **kwargs)
        else:
            raise ValueError(f"Unknown method '{method_name}'. Available methods: {', '.join(method_map.keys())}")

    def get_available_methods(self):
        return {
            'direct': ['gauss_elimination', 'gauss_jordan', 'doolittle_lu', 'crout_lu', 'cholesky'],
            'iterative': ['gauss_seidel', 'jacobi']
        }


class SymbolicSolverFactory(AbstractSolverFactory):

    def create_gauss_elimination(self, n, A, b, **kwargs):
        return SymGaussElimination(n, A, b)

    def create_gauss_jordan(self, n, A, b, **kwargs):
        return SymGaussJordan(n, A, b)

    def create_doolittle_lu(self, n, A, b, **kwargs):
        return SymDoolittleLUDecomposition(n, A, b)

    def create_crout_lu(self, n, A, b, **kwargs):
        return SymCroutLUDecomposition(n, A, b)

    def create_cholesky(self, n, A, b, **kwargs):
        return SymCholeskyLUDecomposition(n, A, b)

    def create_gauss_seidel(self, n, A, b, **kwargs):
        raise NotImplementedError("Symbolic iterative methods not yet implemented")

    def create_jacobi(self, n, A, b, **kwargs):
        raise NotImplementedError("Symbolic iterative methods not yet implemented")

    def create_solver(self, method_name, *args, **kwargs):
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
            return method_map[method_name](*args, **kwargs)
        else:
            raise ValueError(f"Unknown method '{method_name}'. Available methods: {', '.join(method_map.keys())}")

    def get_available_methods(self):
        return {
            'direct': ['gauss_elimination', 'gauss_jordan', 'doolittle_lu', 'crout_lu', 'cholesky'],
            'iterative': ['gauss_seidel', 'jacobi']
        }
        
        
class NonLinearSolverFactory:
    def create_bisection(self, func, xl, xu, precision=5, max_iter=50, tolerance=1e-5):
        return Bisection(func, xl, xu, precision=precision, max_iter=max_iter, tolerance=tolerance)
    
    def create_false_position(self, func, xl, xu, precision=5, max_iter=50, tolerance=1e-5):
        return FalsePosition(func, xl, xu, precision=precision, max_iter=max_iter, tolerance=tolerance)
    
    def create_fixed_point(self, func, x0, precision=5, max_iter=50, tolerance=1e-5):
        return FixedPoint(func, x0, precision=precision, max_iter=max_iter, tolerance=tolerance)
    
    def create_newton_raphson(self, func, x0, precision=5, max_iter=50, tolerance=1e-5):
        return OriginalNewtonRaphson(func, x0, precision=precision, max_iter=max_iter, tolerance=tolerance)
    
    def create_modified_newton_raphson(self, func, x0, precision=5, max_iter=50, tolerance=1e-5):
        return ModifiedNewtonRaphson(func, x0, precision=precision, max_iter=max_iter, tolerance=tolerance)
    
    def create_secant_method(self, func, x0, x1, precision=5, max_iter=50, tolerance=1e-5):
        return SecantMethod(func, x0, x1, precision=precision, max_iter=max_iter, tolerance=tolerance)
    
    def create_solver(self, method_name, *args, **kwargs):
        method_name = method_name.lower().replace(' ', '_')
        
        method_map = {
            'bisection': self.create_bisection,
            'false_position': self.create_false_position,
            'fixed_point': self.create_fixed_point,
            'newton_raphson': self.create_newton_raphson,
            'modified_newton_raphson': self.create_modified_newton_raphson,
            'secant_method': self.create_secant_method,
        }
        
        if method_name in method_map:
            return method_map[method_name](*args, **kwargs)
        else:
            raise ValueError(f"Unknown method '{method_name}'. Available methods: {', '.join(method_map.keys())}")
        
    def get_available_methods(self):
        return [
            'bisection',
            'false_position',
            'fixed_point',
            'newton_raphson',
            'modified_newton_raphson',
            'secant_method'
        ]


if __name__ == "__main__":
    print("=== Numerical Solver Factory ===")
    num_factory = NumericalSolverFactory()
    A = [[4, -1, 0], [-1, 4, -1], [0, -1, 4]]
    b = [15, 10, 10]
    solver = num_factory.create_solver('gauss_elimination', A, b, precision=5)
    print(f"Solution: {solver.solve()}")

    print("\n=== Symbolic Solver Factory ===")
    sym_factory = SymbolicSolverFactory()
    # Test with symbolic values (strings)
    A_sym = [["a", "b"], ["c", "d"]]
    b_sym = ["p", "q"]
    sym_solver = sym_factory.create_solver('gauss_elimination', n=2, A=A_sym, b=b_sym)
    print(f"Solution:\n{sym_solver.solve()}")

    print("\n=== Available Methods ===")
    print("Numerical:", num_factory.get_available_methods())
    print("Symbolic:", sym_factory.get_available_methods())

