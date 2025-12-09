import numpy as np
import math
from abc import ABC, abstractmethod

from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, convert_xor
from typing_extensions import override
import sympy as sp


class RootSolver(ABC):
    def __init__(self, func_str, precision=10, max_iter=50, tolerance=1e-5):
        self.func_str = func_str
        self.precision = precision
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.steps = []

        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))

        try:
            self.expr = parse_expr(self.func_str, transformations=transformations)
        except:
            raise ValueError("couldn't parse the expression")

        symbols_found = list(self.expr.free_symbols)

        if len(symbols_found) == 0:
            self.variable = sp.Symbol('x')

        elif len(symbols_found) == 1:
            self.variable = symbols_found[0]
        else:
            raise ValueError(f"Too many variables found: {symbols_found}. Please use only one.")

        self.f_calc = sp.lambdify(self.variable, self.expr, "numpy")

    def f(self, value):
        try:
            return self.f_calc(value)
        except Exception as e:
            raise ValueError(f"Math Error at value {value}: {e}")

    def calculate_error(self, x_new, x_old):
        if x_new == 0:
            return 0
        else:
            return abs(((x_new - x_old) / x_new) * 100)

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def draw(self):
        pass


class BracketingSolver(RootSolver):
    def __init__(self, func_str, xl, xu, precision=5, max_iter=50, tolerance=1e-5):
        super().__init__(func_str, precision, max_iter, tolerance)
        self.xl = float(xl)
        self.xu = float(xu)

    def check_bracket(self):
        if self.f(self.xl) * self.f(self.xu) >= 0:
            raise ValueError("Root not bracketed. f(xl) and f(xu) must have opposite signs.")


class OpenSolver(RootSolver):
    pass


class Bisection(BracketingSolver):
    pass


class FalsePosition(BracketingSolver):
    pass


class FixedPoint(OpenSolver):
    pass


class OriginalNewtonRaphson(OpenSolver):
    pass


class ModifiedNewtonRaphson(OpenSolver):
    pass


class SecantMethod(OpenSolver):
    pass
