from flask import Flask, request, jsonify
from flask_cors import CORS

from SolverFactory import NumericalSolverFactory, SymbolicSolverFactory, AbstractSolverFactory, NonLinearSolverFactory
from mainSymbols import *
from BackEnd.linearMethods import *
from BackEnd.nonlinearMethods import *
from Plotter import Plotter
import numpy as np
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)

@app.route('/solve', methods=['POST'])
def solve_system():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(data)
        except:
            return jsonify({'error': 'The input is not valid JSON'}), 400

        A = np.array(data['A']) if data['A'] else None
        b = np.array(data['b']) if data['b'] else None
        mode = data.get('mode')
        method = data.get('method')
        precision = data.get('precision', 5)
        initial_guess = data.get('initial_guess')
        num_of_ites = data.get('num_of_ites')
        abs_rel_error = data.get('abs_rel_error')
        withScaling = data.get('withScaling', False)
        n = data.get('n')
        factory: AbstractSolverFactory = None
        solver = None
        if mode == "numerical":
            factory = NumericalSolverFactory()
            # Check if method is iterative to pass correct parameters
            iterative_methods = ['gauss_seidel', 'jacobi']
            if method in iterative_methods:
                # Iterative methods: precision, initial_guess, num_of_ites, abs_rel_error
                solver = factory.create_solver(
                    method,
                    A,
                    b,
                    precision=precision,
                    initial_guess=initial_guess,
                    num_of_ites=num_of_ites,
                    abs_rel_error=abs_rel_error
                )
            else:
                # Direct methods: precision and withScaling
                solver = factory.create_solver(
                    method,
                    A,
                    b,
                    precision=precision,
                    withScaling=withScaling
                )

        if mode == "symbolic":
            factory = SymbolicSolverFactory()
            # For symbolic mode, use raw string arrays from frontend (not numpy arrays)
            A_symbolic = data['A']
            b_symbolic = data['b']
            print(f"Symbolic mode - A: {A_symbolic}")
            print(f"Symbolic mode - b: {b_symbolic}")
            print(f"Symbolic mode - n: {n}")
            solver = factory.create_solver(method, n, A_symbolic, b_symbolic)

        startTime = time.time()

        try:
            solution = solver.solve()

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        endTime = time.time()
        executionTime = endTime - startTime

        raw_steps = getattr(solver, 'steps', [])

        # Convert all steps (including SymPy objects) to serializable form
        formatted_steps = to_serializable(raw_steps)

        # Convert solution to JSON-serializable format
        solution_list = to_serializable(solution)

        return jsonify({
            'solution': solution_list,
            'executionTime': executionTime,
            'num_of_ites': getattr(solver, 'num_of_ites', None),
            'steps': formatted_steps,
            'steps_descriptions': to_serializable(getattr(solver, 'describitive_steps', None)),
            'Xs_steps': to_serializable(getattr(solver, 'Xs_steps', None)),
            'Ys_steps': to_serializable(getattr(solver, 'Ys_steps', None)),
            'message' : getattr(solver, 'message', "")
        })
        
@app.route('/solve-root', methods=['POST'])
def solve_nonlinear():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(data)
        except:
            return jsonify({'error': 'The input is not valid JSON'}), 400
        
        func = data.get('func')
        method = data.get('method')
        
        # Parameters for Bracketing Methods
        xl = data.get('xl')
        xu = data.get('xu')
        # Parameters for Open Methods
        x0 = data.get('x0')
        x1 = data.get('x1')
        
        precision = data.get('precision', 5)
        max_iter = data.get('max_iter', 50)
        tolerance = data.get('tolerance', 1e-5)

        factory: NonLinearSolverFactory = None
        solver = None
        
        if method in ['bisection', 'false_position']:
            factory = NonLinearSolverFactory()
            solver = factory.create_solver(
                method,
                func,
                xl,
                xu,
                precision=precision,
                max_iter=max_iter,
                tolerance=tolerance
            )
        elif method in ['fixed_point', 'newton_raphson', 'modified_newton_raphson']:
            factory = NonLinearSolverFactory()
            solver = factory.create_solver(
                method,
                func,
                x0,
                precision=precision,
                max_iter=max_iter,
                tolerance=tolerance
            )
        elif method == 'secant_method':
            factory = NonLinearSolverFactory()
            solver = factory.create_solver(
                method,
                func,
                x0,
                x1,
                precision=precision,
                max_iter=max_iter,
                tolerance=tolerance
            )
        
        startTime = time.time()

        try:
            solution = solver.solve()

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        endTime = time.time()
        executionTime = endTime - startTime
        
        return jsonify({
            'status': solution.get('status'),
            'executionTime': executionTime,
            'root':to_serializable(solution.get('root')),
            'steps': to_serializable(solution.get('steps')),
            'message' : solution.get('message', "")
        })
        
        
@app.route('/plot', methods=['POST'])
def plot_function():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(data)
        except:
            return jsonify({'error': 'The input is not valid JSON'}), 400
        
        func_str = data.get('func')
        x_min = data.get('x_min', -10.0)
        x_max = data.get('x_max', 10.0)
        method_type = data.get('method_type', 'bisection')
        
        plot_data = Plotter.get_plot_data(func_str, x_min, x_max, method_type)
        
        return jsonify(plot_data)
        
# Helper to convert any value to JSON-serializable format
def to_serializable(val):
    if val is None:
        return None
    if isinstance(val, (int, float, str, bool)):
        return val
    if hasattr(val, 'tolist'):
        # NumPy arrays / SymPy matrices
        return to_serializable(val.tolist())
    if isinstance(val, dict):
        return {to_serializable(k): to_serializable(v) for k, v in val.items()}
    # Handle any iterable (list, tuple, etc.), but avoid treating strings as iterables
    try:
        if not isinstance(val, (str, bytes)) and hasattr(val, '__iter__'):
            return [to_serializable(item) for item in val]
    except TypeError:
        pass
    # Fallback: SymPy objects and everything else
    return str(val)

if __name__ == '__main__':
     app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
