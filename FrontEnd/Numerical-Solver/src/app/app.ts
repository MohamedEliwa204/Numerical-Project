import { CommonModule } from '@angular/common';
import { Component, effect, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Sidebar } from './sidebar/sidebar';
import { MatrixInput } from './matrix-input/matrix-input';
import { Parameters } from './parameters/parameters';
import { ResponseData } from './models/response-data';
import { RequestData } from './models/request-data';
import { SolverService } from './services/solver-service';

@Component({
  selector: 'app-root',
  imports: [CommonModule, Sidebar, MatrixInput, Parameters],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  selectedMethod = signal<MethodType>('Gauss Elimination');
  numEquations = signal(3);

  matrixA = signal<number[][]>([]);
  vectorB = signal<number[]>([]);
  precision = signal<number>(4);

  solution = signal<string[] | null>(null);
  executionTime = signal(0);
  iterations = signal(0);

  constructor(
    private api: SolverService
  ) { }

  onMatrixDataChange(data: { A: number[][], B: number[], precision: number }) {
    this.matrixA.set(data.A);
    this.vectorB.set(data.B);
    this.precision.set(data.precision);
  }

  onSolve(params: SolverParams) {
    // const startTime = performance.now();

    let methodUsed: string = 'GaussElimination'
    switch (this.selectedMethod()) {
      case 'Gauss Elimination':
        methodUsed = 'GaussElimination'
        break;
      case 'Gauss-Jordan':
        methodUsed = 'GaussJordan'
        break;
      case 'LU Decomposition':
        switch (params.luForm) {
          case 'Doolittle':
            methodUsed = 'DoolittleLUDecomposition'
            break;
          case 'Crout':
            methodUsed = 'CroutLUDecomposition'
            break;
          case 'Cholesky':
            methodUsed = 'CholeskyLUDecomposition'
            break;
        }
        break;
      case 'Gauss-Seidel':
        methodUsed = 'GaussSeidel'
        break;
      case 'Jacobi-Iteration':
        methodUsed = 'JacobiIteration'
        break;
    }

    console.log('Solving with:', methodUsed);
    console.log('Matrix A:', this.matrixA());
    console.log('Vector B:', this.vectorB());
    console.log('Precision: ', this.precision());
    console.log('Params:', params);

    let dataSent: RequestData = {
      A: this.matrixA(),
      b: this.vectorB(),
      method: methodUsed,
      precision: this.precision(),
      withScaling: params.useScaling,
      initial_guess: params.initialGuess,
      num_of_ites: params.maxIterations,
      abs_rel_error: params.tolerance
    }

    this.api.getSolution(dataSent).subscribe({
      next: (response) => {
        console.log('Response from Backend: ', response);

        const result = response.solution.map((val) => {
          return val.toFixed(this.precision())
        })
        this.solution.set(result);

        this.iterations.set((this.selectedMethod() === 'Gauss-Seidel' || this.selectedMethod() === 'Jacobi-Iteration')
          ? params.maxIterations : 0);

        // const endTime = performance.now();
        this.executionTime.set(parseFloat(response.executionTime.toFixed(12)));
      },
      error: (error) => {
        console.error('Error Sending Solution Request:', error.error.error);
      }
    })
  }
}
