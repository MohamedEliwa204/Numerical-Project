from dataclasses import asdict

import numpy as np
import math
from abc import ABC, abstractmethod

from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, convert_xor
from typing_extensions import override
import sympy as sp
from IterationStep import IterationStep


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

    def check_bracket(self, xl, xu):
        return self.f(xl) * self.f(xu) < 0


class OpenSolver(RootSolver):
    pass


class Bisection(BracketingSolver):
    @override
    def solve(self):
        self.steps = []
        if not self.check_bracket(self.xl, self.xu):
            return {
                "status": "error",
                "root": None,
                "steps": [],
                "message": f"Initialization Failed: Root is not bracketed between {self.xl} and {self.xu}. f(xl)={self.f(self.xl):.4f}, f(xu)={self.f(self.xu):.4f}"
            }
        xl, xu = self.xl, self.xu
        xr_old = xl
        xr = xl

        for i in range(self.max_iter):

            try:
                xr = (xl + xu) / 2
                fxr = self.f(xr)
                fxl = self.f(xl)
                fxu = self.f(xu)

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(xr, xr_old)
            except Exception as e:
                # Catch Math Errors (like Overflow/NaN) in the middle
                return {
                    "status": "error",
                    "root": xr,
                    "steps": [asdict(s) for s in self.steps],  # Return what we have so far
                    "message": f"Math Error at iteration {i}: {str(e)}"
                }

            if fxl * fxu > 0:
                return {
                    "status": "error",
                    "root": xr,
                    "steps": [asdict(s) for s in self.steps],
                    "message": f"Bracket Lost at iteration {i}. Function may be discontinuous."
                }

            if fxl * fxr < 0:
                desc = "Root in Left sub-interval, we replaced xu by xr."
                next_xl, next_xu = xl, xr
            elif fxl * fxr > 0:
                desc = "Root in Right sub-interval, we replaced xl by xr."
                next_xl, next_xu = xr, xu
            else:
                desc = "Exact root found."
                error = 0.0
                next_xl, next_xu = xr, xr

            step_traces = [
                {"x": [xl, xl], "y": [0, fxl], "type": "scatter", "mode": "lines",
                 "line": {"color": "green", "dash": "dash"}, "name": "xl"},
                {"x": [xu, xu], "y": [0, fxu], "type": "scatter", "mode": "lines",
                 "line": {"color": "green", "dash": "dash"}, "name": "xu"},
                {"x": [xr], "y": [fxr], "type": "scatter", "mode": "markers", "marker": {"color": "red", "size": 8},
                 "name": "xr"}
            ]

            step_record = IterationStep(
                step_number=i,
                numericals={
                    "xl": round(xl, self.precision),
                    "xu": round(xu, self.precision),
                    "xr": round(xr, self.precision),
                    "f(xr)": round(fxr, self.precision),
                    "error": round(error, self.precision)
                },
                description=desc,
                plot_data=step_traces
            )

            self.steps.append(step_record)
            if self.calculate_error(xr, xr_old) < self.tolerance:
                return {
                    "status": "success",
                    "root": xr,
                    "steps": [asdict(s) for s in self.steps],
                    "message": "Converged successfully."
                }
            xl, xu = next_xl, next_xu
            xr_old = xr

        return {
            "status": "success",  # Or "warning"
            "root": xr,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached without full convergence."
        }


class FalsePosition(BracketingSolver):
    @override
    def solve(self):
        self.steps = []
        if not self.check_bracket(self.xl, self.xu):
            return {
                "status": "error",
                "root": None,
                "steps": [],
                "message": f"Initialization Failed: Root is not bracketed between {self.xl} and {self.xu}. f(xl)={self.f(self.xl):.4f}, f(xu)={self.f(self.xu):.4f}"
            }
        xl, xu = self.xl, self.xu
        xr_old = xl
        xr = xl
        for i in range(self.max_iter):
            try:

                fxl = self.f(xl)
                fxu = self.f(xu)
                xr = ((xl * fxu) - (xu - fxl)) / (fxu - fxl)
                fxr = self.f(xr)

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(xr, xr_old)
            except Exception as e:

                return {
                    "status": "error",
                    "root": xr,
                    "steps": [asdict(s) for s in self.steps],  # Return what we have so far
                    "message": f"Math Error at iteration {i}: {str(e)}"
                }

            if fxl * fxu > 0:
                return {
                    "status": "error",
                    "root": xr,
                    "steps": [asdict(s) for s in self.steps],
                    "message": f"Bracket Lost at iteration {i}. Function may be discontinuous."
                }

            if fxl * fxr < 0:
                desc = "Root in Left sub-interval, we replaced xu by xr."
                next_xl, next_xu = xl, xr
            elif fxl * fxr > 0:
                desc = "Root in Right sub-interval, we replaced xl by xr."
                next_xl, next_xu = xr, xu
            else:
                desc = "Exact root found."
                error = 0.0
                next_xl, next_xu = xr, xr
            step_traces = [
                # Vertical Line at xl
                {"x": [xl, xl], "y": [0, fxl], "type": "scatter", "mode": "lines",
                 "line": {"color": "green", "dash": "dash"}, "name": "xl"},

                # Vertical Line at xu
                {"x": [xu, xu], "y": [0, fxu], "type": "scatter", "mode": "lines",
                 "line": {"color": "green", "dash": "dash"}, "name": "xu"},

                # *** THE SECANT LINE *** (Blue Solid Line)
                # Connects point (xl, f(xl)) to (xu, f(xu))
                {"x": [xl, xu], "y": [fxl, fxu], "type": "scatter", "mode": "lines",
                 "line": {"color": "blue", "width": 2}, "name": "Secant Line"},

                # The Root Guess (Red Dot)
                {"x": [xr], "y": [fxr], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "xr"}
            ]
            step_record = IterationStep(
                step_number=i,
                numericals={
                    "xl": round(xl, self.precision),
                    "xu": round(xu, self.precision),
                    "xr": round(xr, self.precision),
                    "f(xr)": round(fxr, self.precision),
                    "error": round(error, self.precision)
                },
                description=desc,
                plot_data=step_traces
            )
            self.steps.append(step_record)
            if error < self.tolerance:
                return {
                    "status": "success",
                    "root": xr,
                    # Convert objects to dicts for JSON
                    "steps": [asdict(s) for s in self.steps],
                    "message": "Converged successfully."
                }

            xl, xu = next_xl, next_xu
            xr_old = xr

        return {
            "status": "success",
            "root": xr,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached."
        }



class FixedPoint(OpenSolver):
    pass


class OriginalNewtonRaphson(OpenSolver):
    pass


class ModifiedNewtonRaphson(OpenSolver):
    pass


class SecantMethod(OpenSolver):
    pass
