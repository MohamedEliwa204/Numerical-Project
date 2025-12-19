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
            
        correctSFs = self.number_of_significant_figures(ea, xr)
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
        # ----- Add y=x and y=g(x) curves -----
        # Create x-range around current guess
        # x_min = xr_old - 5
        # x_max = xr_old + 5
        x_min=-10
        x_max=10
        xs = np.linspace(x_min, x_max, 200)

        # g(x) values
        try:
            ys_g = [self.f(v) for v in xs]
        except Exception:
            ys_g = [None for _ in xs]  # safe fallback

        # Add y=x line
        step_traces.append({
            "x": xs.tolist(),
            "y": xs.tolist(),
            "type": "scatter",
            "mode": "lines",
            "line": {"color": "blue", "width": 2},
            "name": "y = x"
        })

        # Add g(x) curve
        step_traces.append({
            "x": xs.tolist(),
            "y": ys_g,
            "type": "scatter",
            "mode": "lines",
            "line": {"color": "green", "width": 2},
            "name": "y = g(x)"
        })

        step_record = IterationStep(
            step_number=current_iteration,
            numericals={
                "xr_old": xr_old,
                "xr_new": xr,
                "g(xr_old)": xr,
                "error": ea,
                "correctSFs": correctSFs
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
                correctSFs = self.number_of_significant_figures(ea, xr)

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
                # ----- Add y=x and y=g(x) curves -----


                # Create x-range around current guess
                # x_min = xr_old - 5
                # x_max = xr_old + 5
                x_min=-10
                x_max=10
                xs = np.linspace(x_min, x_max, 200)

                # g(x) values
                try:
                    ys_g = [self.f(v) for v in xs]
                except Exception:
                    ys_g = [None for _ in xs]  # safe fallback

                # Add y=x line
                step_traces.append({
                    "x": xs.tolist(),
                    "y": xs.tolist(),
                    "type": "scatter",
                    "mode": "lines",
                    "line": {"color": "blue", "width": 2},
                    "name": "y = x"
                })

                # Add g(x) curve
                step_traces.append({
                    "x": xs.tolist(),
                    "y": ys_g,
                    "type": "scatter",
                    "mode": "lines",
                    "line": {"color": "green", "width": 2},
                    "name": "y = g(x)"
                })

                step_record = IterationStep(
                    step_number=current_iteration,
                    numericals={
                        "xr_old": xr_old,
                        "xr_new": xr_new,
                        "g(xr_old)": xr_new,
                        "error": ea,
                        "correctSFs": correctSFs
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

        if ea <= self.tolerance:
            return {
                "status": "success",
                "root": xr,
                "steps": [asdict(s) for s in self.steps],
                "message": "Converged successfully."
            }
        else:
            return {
                "status": "failure",
                "root": xr,
                "steps": [asdict(s) for s in self.steps],
                "message": f"Max iterations ({self.max_iter}) reached without convergence to tolerance {self.tolerance}."
            }



class OriginalNewtonRaphson(OpenSolver):
    @override
    def solve(self):
        self.steps = []

        # Differentiate the expression
        derivative_expr = sp.diff(self.expr, self.variable)

        # Convert derivative to a numpy function
        first_derivative_calc = sp.lambdify(self.variable, derivative_expr, "numpy")

        def f_deriv(value):
            try:
                return first_derivative_calc(value)
            except Exception as e:
                raise ValueError(f"Math Error in derivative at {value}: {e}")

        x_current = self.x0
        x_old = x_current # Initialized just to calculate the first error
        x_new = x_current

        for i in range(self.max_iter):
            try:
                fx = self.round_significant(self.f(x_current))

                # Check for exact root
                if fx == 0:
                    self.steps.append(IterationStep(
                        step_number=i,
                        numericals={
                            "x_old": x_old,
                            "x_current": x_current,
                            "f(x_current)": 0,
                            "f'(x_current)": 0,
                            "x_new": x_current,
                            "error": 0,
                            "correctSFs": self.number_of_significant_figures(0, x_current)
                        },
                        description="Exact root found.",
                        plot_data=[{"x": [x_current], "y": [0], "type": "scatter", "mode": "markers", "marker": {"color": "green", "size": 10}, "name": "Exact Root"}]
                    ))
                    return {
                        "status": "success",
                        "root": x_current,
                        "steps": [asdict(s) for s in self.steps],
                        "message": "Exact root found."
                    }

                fdx = self.round_significant(f_deriv(x_current))

                if fdx == 0:
                    return {
                        "status": "error",
                        "root": x_current,
                        "steps": [asdict(s) for s in self.steps],
                        "message": f"Derivative is zero at x={x_current}. Cannot divide by zero."
                    }

                x_new = self.round_significant(x_current - (fx / fdx))

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(x_new, x_current)

                correctSFs = self.number_of_significant_figures(error, x_new)

            except Exception as e:
                return {
                    "status": "error",
                    "root": x_new,
                    "steps": [asdict(s) for s in self.steps],
                    "message": f"Math Error at iteration {i}: {str(e)}"
                }

            # Line Visualizing
            step_traces = [
                # The Curve point
                {"x": [x_current], "y": [fx], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "Current Point"},

                # The Tangent Line
                {"x": [x_current, x_new], "y": [fx, 0], "type": "scatter", "mode": "lines",
                 "line": {"color": "green", "dash": "dash", "width": 2}, "name": "Tangent Line"},

                # The New Root Estimate
                {"x": [x_new], "y": [0], "type": "scatter", "mode": "markers",
                 "marker": {"color": "blue", "size": 8}, "name": "New Estimate"}
            ]

            step_record = IterationStep(
                step_number = i,
                numericals = {
                    "x_old": x_old,
                    "x_current": x_current,
                    "f(x_current)": fx,
                    "f'(x_current)": fdx,
                    "x_new": x_new,
                    "error": error,
                    "correctSFs": correctSFs
                },
                description=f"Tangent at {x_current} intersects axis at {x_new}",
                plot_data=step_traces
            )

            self.steps.append(step_record)

            # Check Convergence
            if error < self.tolerance:
                return {
                    "status": "success",
                    "root": x_new,
                    "steps": [asdict(s) for s in self.steps],
                    "message": "Converged successfully."
                }

            # Update
            x_old = x_current
            x_current = x_new

        return {
            "status": "failure",
            "root": x_new,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached without convergence to tolerance {self.tolerance}."
        }


class ModifiedNewtonRaphson(OpenSolver):
    @override
    def solve(self):
        self.steps = []

        derivative_expr = sp.diff(self.expr, self.variable)
        second_derivative_expr = sp.diff(derivative_expr, self.variable)

        first_derivative_calc = sp.lambdify(self.variable, derivative_expr, "numpy")
        second_derivative_calc = sp.lambdify(self.variable, second_derivative_expr, "numpy")

        def f_prime(value):
            try:
                return first_derivative_calc(value)
            except Exception as e:
                raise ValueError(f"Math Error in first derivative at {value}: {e}")

        def f_double_prime(value):
            try:
                return second_derivative_calc(value)
            except Exception as e:
                raise ValueError(f"Math Error in second derivative at {value}: {e}")

        x_current = self.x0
        x_old = x_current
        x_new = x_current

        for i in range(self.max_iter):
            try:
                fx = self.round_significant(self.f(x_current))

                if fx == 0:
                    self.steps.append(IterationStep(
                        step_number=i,
                        numericals={
                            "x_old": x_old,
                            "x_current": x_current,
                            "f(x)": 0, "f'(x)": 0, "f''(x)": 0,
                            "x_new": x_current,
                            "error": 0,
                            "correctSFs": self.number_of_significant_figures(0, x_current)
                        },
                        description="Exact root found.",
                        plot_data=[{"x": [x_current], "y": [0], "type": "scatter", "mode": "markers", "marker": {"color": "green", "size": 10}, "name": "Exact Root"}]
                    ))
                    return {
                        "status": "success",
                        "root": x_current,
                        "steps": [asdict(s) for s in self.steps],
                        "message": "Exact root found."
                    }
                fdx = self.round_significant(f_prime(x_current))
                f2dx = self.round_significant(f_double_prime(x_current))

                denominator = (fdx**2) - (fx * f2dx)

                if denominator == 0:
                    return {
                        "status": "error",
                        "root": x_current,
                        "steps": [asdict(s) for s in self.steps],
                        "message": f"Denominator is zero at x={x_current}."
                    }

                x_new = self.round_significant(x_current - ((fx * fdx) / denominator))

                if i == 0:
                    error = 100.0
                else:
                    error = self.calculate_error(x_new, x_current)

                correctSFs = self.number_of_significant_figures(error, x_new)

            except Exception as e:
                return {
                    "status": "error",
                    "root": x_new,
                    "steps": [asdict(s) for s in self.steps],
                    "message": f"Math Error at iteration {i}: {str(e)}"
                }

            step_traces = [
                {"x": [x_current], "y": [fx], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "Current Point"},

                {"x": [x_current, x_new], "y": [fx, 0], "type": "scatter", "mode": "lines",
                 "line": {"color": "purple", "dash": "dot", "width": 2}, "name": "Modified Step"},

                {"x": [x_new], "y": [0], "type": "scatter", "mode": "markers",
                 "marker": {"color": "blue", "size": 8}, "name": "New Estimate"}
            ]

            step_record = IterationStep(
                step_number=i,
                numericals={
                    "x_old": x_old,
                    "x_current": x_current,
                    "f(x)": fx,
                    "f'(x)": fdx,
                    "f''(x)": f2dx,
                    "x_new": x_new,
                    "error": error,
                    "correctSFs": correctSFs
                },
                description=f"Modified NR step from {x_current} to {x_new}",
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

            x_old = x_current
            x_current = x_new

        return {
            "status": "failure",
            "root": x_new,
            "steps": [asdict(s) for s in self.steps],
            "message": f"Max iterations ({self.max_iter}) reached without convergence to tolerance {self.tolerance}."
        }


class SecantMethod(OpenSolver):
    @override
    def solve(self):
        self.steps = []
        x0 = self.x0
        x1 = self.x1

        if x1 is None or x0 == x1:
            return {
                "status": "error",
                "root": None,
                "steps": [],
                "message": "Initialization Failed: Secant Method requires two distinct initial guesses (x0 and x1)."
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
                    
                correctSFs = self.number_of_significant_figures(error, x_new)

            except Exception as e:
                return {
                "status": "error",
                "root": x_new,
                "steps": [asdict(s) for s in self.steps],  # Return what we have so far
                "message": f"Math Error at iteration {i}: {str(e)}"
            }

            m = (f_xcur - f_xold) / (x_cur - x_old)
            b = f_xold - m * x_old
            
            x_min = min(x_old, x_cur, x_new)
            x_max = max(x_old, x_cur, x_new)
            
            x_line = [x_min, x_max]
            y_line = [m*x_min + b, m*x_max + b]

            step_traces = [
                # old point
                {"x": [x_old], "y": [f_xold], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "x_old"},
                # current point
                {"x": [x_cur], "y": [f_xcur], "type": "scatter", "mode": "markers",
                 "marker": {"color": "red", "size": 8}, "name": "x_cur"},
                # new approximation point
                {"x": [x_new], "y": [0], "type": "scatter", "mode": "markers",
                 "marker": {"color": "green", "size": 8}, "name": "x_new"},
                # secant line
                {"x": x_line, "y": y_line, "type": "scatter", "mode": "lines",
                 "line": {"color": "black", "width": 2, "dash": "dash"}, "name": "Secant Line"}
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
            "message": f"Max iterations ({self.max_iter}) reached without convergence to tolerance {self.tolerance}."
        }