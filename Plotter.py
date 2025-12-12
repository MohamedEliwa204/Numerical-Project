import numpy as np
import sympy as sp
from sympy import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, convert_xor

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


class Plotter:
    @staticmethod
    def get_plot_data(func_str: str, x_min: float = -10.0, x_max: float = 10.0, method_type: str = "bisection"):
        transformations = (standard_transformations + (implicit_multiplication_application, convert_xor))

        try:
            expr = parse_expr(func_str, local_dict=MATH_LOCAL_DICT, transformations=transformations)

            symbols = list(expr.free_symbols)
            if len(symbols) > 1:
                return {"error": "Equation contains too many variables. Please use only one."}
            var = symbols[0] if symbols else sp.Symbol('x')


            f_calc = sp.lambdify(var, expr, modules="numpy")

        except Exception as e:
            return {"error": f"Syntax Error: {str(e)}"}

        raw_x = np.linspace(float(x_min), float(x_max), 400)

        clean_x = []
        clean_y = []

        for x_val in raw_x:
            try:

                y_val = float(f_calc(x_val))


                if np.isnan(y_val) or np.isinf(y_val):
                    continue

                clean_x.append(x_val)
                clean_y.append(y_val)
            except Exception:

                continue

        if not clean_x:
            return {"error": "Function is undefined in this range."}


        traces = []

        #trace1: the user function
        traces.append({
            "x": clean_x,
            "y": clean_y,
            "type": "scatter",
            "mode": "lines",
            "name": "g(x)" if method_type == "fixed_point" else "f(x)",
            "line": {"color": "#1f77b4", "width": 3} # Standard Blue
        })

        #trace 2: The reference line
        if method_type == "fixed_point":
            traces.append({
                "x": clean_x,
                "y": clean_x, # y equals x
                "type": "scatter",
                "mode": "lines",
                "name": "y = x",
                "line": {"color": "#ff7f0e", "dash": "dash", "width": 2}
            })
        else:
            traces.append({
                "x": [min(clean_x), max(clean_x)],
                "y": [0, 0],
                "type": "scatter",
                "mode": "lines",
                "name": "y = 0",
                "line": {"color": "black", "width": 1}
            })


        return {
            "data": traces,
            "layout": {
                "title": f"Plot of {func_str}",
                "xaxis": {"title": str(var)},
                "yaxis": {"title": "Value"},
                "showlegend": True,
                "autosize": True,
                "margin": {"l": 40, "r": 20, "t": 40, "b": 40}
            }
        }
