from dataclasses import asdict

import numpy as np
import math
from abc import ABC, abstractmethod

from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, convert_xor
from typing_extensions import override
import sympy as sp
from IterationStep import IterationStep

# Local dictionary for common math functions and constants
MATH_LOCAL_DICT = {
    'e': sp.E,
    'pi': sp.pi,
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'cot': sp.cot,
    'sec': sp.sec,
    'csc': sp.csc,
    'asin': sp.asin,
    'acos': sp.acos,
    'atan': sp.atan,
    'sinh': sp.sinh,
    'cosh': sp.cosh,
    'tanh': sp.tanh,
    'exp': sp.exp,
    'log': sp.log,
    'ln': sp.ln,
    'sqrt': sp.sqrt,
    'abs': sp.Abs,
}


class RootSolver(ABC):
    def __init__(self, func_str, precision=10, max_iter=50, tolerance=1e-5):
        self.func_str = func_str
        self.precision = precision
        self.max_iter = max_iter
        self.tolerance = tolerance
        self.steps = []

        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))

        try:
            self.expr = parse_expr(self.func_str, local_dict=MATH_LOCAL_DICT, transformations=transformations)
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
        
    def number_of_significant_figures(self, error, x_new):
        if error > 5:
            m = 0
        elif error == 0: # Exact root found
            s = str(abs(x_new))
            if '.' in s:
                integer_part, fractional_part = s.split('.')
                
                if x_new < 1:
                    integer_digits = 0  # No integer digits for numbers < 1
                    fractional_digits = len(fractional_part.lstrip('0'))  # Count digits in fractional part excluding leading zeros
                else:
                    integer_digits = len(integer_part)
                    temp = int(fractional_part)
                    fractional_digits = len(fractional_part) if temp != 0 else 0

                m = integer_digits + fractional_digits
            else :
                m = len(s)
        else:
            m = max(math.floor(2 - math.log10(2*error)), 0)
        return m

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
