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
        
    def number_of_significant_figures(self, error):
        if error > 5:
            m = 0
        elif error == 0: # Exact root found
            m = self.precision
        else:
            m = math.floor(2 - math.log10(2*error))
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




class BracketingSolver(RootSolver):
    def __init__(self, func_str, xl, xu, precision=5, max_iter=50, tolerance=1e-5):
        super().__init__(func_str, precision, max_iter, tolerance)
        self.xl = float(xl)
        self.xu = float(xu)

    def check_bracket(self, xl, xu):
        return self.f(xl) * self.f(xu) < 0


class OpenSolver(RootSolver):
    def __init__(self, func_str, x0, x1=None, precision=5, max_iter=50, tolerance=1e-5):
        super().__init__(func_str, precision, max_iter, tolerance)
        self.x0 = float(x0)
        self.x1 = float(x1) if x1 is not None else None # additional point for secant method


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
                xr = self.round_significant((xl + xu) / 2)
                fxr = self.round_significant(self.f(xr))
                fxl = self.round_significant(self.f(xl))
                fxu = self.round_significant(self.f(xu))

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(xr, xr_old)
                    
                correctSFs = self.number_of_significant_figures(error)
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
                    "xl": self.round_significant(xl),
                    "xu": self.round_significant(xu),
                    "xr": self.round_significant(xr),
                    "f(xr)": self.round_significant(fxr),
                    "error": error,
                    "correctSFs": correctSFs
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

                fxl = self.round_significant(self.f(xl))
                fxu = self.round_significant(self.f(xu))
                xr = self.round_significant(((xl * fxu) - (xu - fxl)) / (fxu - fxl))
                fxr = self.round_significant(self.f(xr))

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(xr, xr_old)
                    
                correctSFs = self.number_of_significant_figures(error)
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
                    "xl": self.round_significant(xl),
                    "xu": self.round_significant(xu),
                    "xr": self.round_significant(xr),
                    "f(xr)": self.round_significant(fxr),
                    "error": error,
                    "correctSFs": correctSFs
                },
                description=desc,
                plot_data=step_traces
            )
            self.steps.append(step_record)
            if error < self.tolerance:
                return {
                    "status": "success",
                    "root": xr,

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
    def solve(self):
        self.steps = []
        xr_old = self.x0
        current_iteration = 0
        try:
            xr = self.round_significant(self.f(xr_old))
        except Exception as e:
            return {
                "status": "error",
                "root": None,
                "steps": [],
                "message": f"Math Error at initial evaluation: {str(e)}"
            }

        try:
            ea=self.calculate_error(xr, xr_old)
        except Exception:
            ea=100.0
        #for first itteration
        step_traces = [
            # vertical line from (xr_old, xr_old) to (xr_old, g(xr_old))
            {"x": [xr_old, xr_old],
             "y": [xr_old, xr],
             "type": "scatter",
             "mode": "lines",
             "line": {"color": "red", "width": 2},
             "name": f"Iteration {current_iteration} vertical"},
            # horizontal line from (xr_old, g(xr_old)) to (g(xr_old), g(xr_old))
            {"x": [xr_old, xr],
             "y": [xr, xr],
             "type": "scatter",
             "mode": "lines",
             "line": {"color": "red", "width": 2},
             "name": f"Iteration {current_iteration} horizontal"}
        ]
        step_record = IterationStep(
            step_number=current_iteration,
            numericals={
                "xr_old": xr_old,
                "xr_new": xr,
                "g(xr_old)": xr,
                "error": ea
            },
            description=f"Iteration {current_iteration}: xr_old={xr_old}, xr_new={xr}",
            plot_data=step_traces
        )

        self.steps.append(step_record)
        current_iteration += 1
        while ea > self.tolerance and current_iteration < self.max_iter:
            xr_old = xr
            try:
                xr_new = self.round_significant(self.f(xr_old))
                ea = self.calculate_error(xr_new, xr_old) if xr_new != 0 else 100.0

                # Build iteration plot traces (staircase)
                step_traces = [
                    {"x": [xr_old, xr_old],
                     "y": [xr_old, xr_new],
                     "type": "scatter",
                     "mode": "lines",
                     "line": {"color": "red", "width": 2},
                     "name": f"Iteration {current_iteration} vertical"},
                    {"x": [xr_old, xr_new],
                     "y": [xr_new, xr_new],
                     "type": "scatter",
                     "mode": "lines",
                     "line": {"color": "red", "width": 2},
                     "name": f"Iteration {current_iteration} horizontal"}
                ]

                step_record = IterationStep(
                    step_number=current_iteration,
                    numericals={
                        "xr_old": xr_old,
                        "xr_new": xr_new,
                        "g(xr_old)": xr_new,
                        "error": ea
                    },
                    description=f"Iteration {current_iteration}: xr_old={xr_old}, xr_new={xr_new}",
                    plot_data=step_traces
                )

                self.steps.append(step_record)
                current_iteration += 1
            except Exception as e:
                return {
                    "status": "error",
                    "root": xr_old,
                    "steps": [asdict(s) for s in self.steps],
                    "message": f"Math Error at iteration {current_iteration}: {str(e)}"
                }

            status = "success" if ea <= self.tolerance else "failure"
            message = "Converged successfully." if ea <= self.tolerance else f"Max iterations ({self.max_iter}) reached."

        return {
            "status": status,
            "root": xr,
            "steps": [asdict(s) for s in self.steps],
            "message": message
        }






class OriginalNewtonRaphson(OpenSolver):
    pass


class ModifiedNewtonRaphson(OpenSolver):
    pass


class SecantMethod(OpenSolver):
    @override
    def solve(self):
        self.steps = []
        x0 = self.x0
        x1 = self.x1

        if x1 is None:
            return {
                "status": "error",
                "root": None,
                "steps": [],
                "message": "Initialization Failed: Secant Method requires two initial guesses (x0 and x1)."
            }

        x_old = x0
        x_cur = x1
        x_new = x1

        for i in range(self.max_iter):
            try:
                f_xold = self.round_significant(self.f(x_old))
                f_xcur = self.round_significant(self.f(x_cur))
                x_new = self.round_significant(x_cur - (f_xcur * (x_old - x_cur)) / (f_xold - f_xcur))
                f_xnew = self.round_significant(self.f(x_new))

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(x_new, x_cur)

            except Exception as e:
                return {
                "status": "error",
                "root": x_new,
                "steps": [asdict(s) for s in self.steps],  # Return what we have so far
                "message": f"Math Error at iteration {i}: {str(e)}"
            }

            step_traces = [
                # old point
                {"x": [x_old], "y": [f_xold], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "x_old"},
                # current point
                {"x": [x_cur], "y": [f_xcur], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "x_cur"},
                # new approximation point
                {"x": [x_new], "y": [0], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "x_new"},
                # secant line
                {"x": [x_old, x_cur], "y": [f_xold, f_xcur], "type": "scatter", "mode": "lines",
                 "line": {"color": "blue", "width": 2, "dash": "dash"}, "name": "Secant Line"}
            ]

            step_record = IterationStep(
                step_number=i,
                numericals={
                    "x0": x_old,
                    "x1": x_cur,
                    "x_new": x_new,
                    "f(x_new)": f_xnew,
                    "error": error
                },
                description=f"Iteration {i}",
                plot_data=step_traces
            )

            self.steps.append(step_record)

            if error < self.tolerance:
                return {
                    "status": "success",
                    "root": x_new,
                    "steps": [asdict(s) for s in self.steps],
                    "message": "Converged successfully."
                }
            
            x_old = x_cur
            x_cur = x_new

        return {
            "status": "failure",
            "root": x_new,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached."
        }