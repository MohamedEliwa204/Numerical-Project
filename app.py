from flask import Flask, request, jsonify
from flask_cors import CORS

from SolverFactory import NumericalSolverFactory, SymbolicSolverFactory, AbstractSolverFactory
from mainSymbols import *
from BackEnd.methods import *
import numpy as np
import time

app = Flask(__name__)
CORS(app)

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
        # match method:
        #     case 'GaussElimination':
        #         solver = GaussElimination(A, b, precision, withScaling)
        #     case 'GaussJordan':
        #         solver = GaussJordan(A, b, precision, withScaling)
        #     case 'DoolittleLUDecomposition':
        #         solver = DoolittleLUDecomposition(A, b, precision, withScaling)
        #     case 'CroutLUDecomposition':
        #         solver = CroutLUDecomposition(A, b, precision)
        #     case 'CholeskyLUDecomposition':
        #         solver = CholeskyLUDecomposition(A, b, precision)
        #     case 'GaussSeidel':
        #         solver = GaussSeidel(A, b, precision, initial_guess, num_of_ites, abs_rel_error)
        #     case 'JacobiIteration':
        #         solver = JacobiIteration(A, b, precision, initial_guess, num_of_ites, abs_rel_error)
        #     case None:
        #         return jsonify({'error': 'Selection of method is required'}), 400

        startTime = time.time()

        try:
            solution = solver.solve()

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        endTime = time.time()
        executionTime = endTime - startTime
        
        """
        result = {
            'solution': solution.tolist(),
            'executionTime': executionTime,
        }
        
        if hasattr(solver, 'num_of_ites'):
            result['num_of_ites'] = solver.num_of_ites
        """

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
        
        
# Helper to convert any value to JSON-serializable format
def to_serializable(val):
    if val is None:
        return None
    if isinstance(val, (int, float, str, bool)):
        return val
    if hasattr(val, 'tolist'):
        # NumPy arrays / SymPy matrices
        return to_serializable(val.tolist())
    # Handle any iterable (list, tuple, etc.), but avoid treating strings as iterables
    try:
        if not isinstance(val, (str, bytes)) and hasattr(val, '__iter__'):
            return [to_serializable(item) for item in val]
    except TypeError:
        pass
    # Fallback: SymPy objects and everything else
    return str(val)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
