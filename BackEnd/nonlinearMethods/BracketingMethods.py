from .BaseFunctions import *

class BracketingSolver(RootSolver):
    def __init__(self, func_str, xl, xu, precision=5, max_iter=50, tolerance=1e-5):
        super().__init__(func_str, precision, max_iter, tolerance)
        self.xl = float(xl)
        self.xu = float(xu)

    def check_bracket(self, xl, xu):
        return self.f(xl) * self.f(xu) < 0



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

            correctSFs = self.number_of_significant_figures(error, xr)
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
            "status": "failure",
            "root": xr,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached without convergence to tolerance {self.tolerance}."
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
                xr = self.round_significant(((xl * fxu) - (xu * fxl)) / (fxu - fxl))
                fxr = self.round_significant(self.f(xr))

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
                
            correctSFs = self.number_of_significant_figures(error, xr)
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
            "status": "failure",
            "root": xr,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached without convergence to tolerance {self.tolerance}."
        }