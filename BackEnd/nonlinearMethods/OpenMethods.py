from .BaseFunctions import *

class OpenSolver(RootSolver):
    def __init__(self, func_str, x0, x1=None, precision=5, max_iter=50, tolerance=1e-5):
        super().__init__(func_str, precision, max_iter, tolerance)
        self.x0 = float(x0)
        self.x1 = float(x1) if x1 is not None else None # additional point for secant method


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
                xr = xr_new
                ea = abs((xr_new - xr_old) / (xr_new if xr_new != 0 else 1e-12)) * 100

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
                    
                correctSFs = self.number_of_significant_figures(error)

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
                    "error": error,
                    "correctSFs": correctSFs
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