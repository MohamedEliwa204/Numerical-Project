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
        withScaling = data.get('scaling', False)
        n = data.get('n')
        factory: AbstractSolverFactory = None
        solver = None
        if mode == "numerical":
            factory = NumericalSolverFactory()
            solver = factory.create_solver(
                method,
                A,
                b,
                precision=precision,
                withScaling=withScaling,
                initial_guess=initial_guess,
                num_of_ites=num_of_ites,
                abs_rel_error=abs_rel_error
            )
        if mode == "symbolic":
            factory = SymbolicSolverFactory()
            solver = factory.create_solver(method, n)
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

        formatted_steps = []
        if raw_steps:
            for step in raw_steps:
                converted_tuple = [x.tolist() if hasattr(x, 'tolist') else x for x in step]
                formatted_steps.append(converted_tuple)
        
        return jsonify({
            'solution': solution.tolist(),
            'executionTime': executionTime,
            'num_of_ites': getattr(solver, 'num_of_ites', None),
            'steps': formatted_steps,
            'steps_descriptions' : getattr(solver, 'describitive_steps', None),
            'Xs_steps' : getattr(solver, 'Xs_steps', None),
            'Ys_steps' : getattr(solver, 'Ys_steps', None)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
