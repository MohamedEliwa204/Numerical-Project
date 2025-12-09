import { CommonModule } from '@angular/common';
import { Component, computed, effect, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Sidebar } from './sidebar/sidebar';
import { MatrixInput } from './matrix-input/matrix-input';
import { Parameters } from './parameters/parameters';
import { ResponseData } from './models/response-data';
import { RequestData } from './models/request-data';
import { SolverService } from './services/solver-service';
import { StepsPanel } from './steps-panel/steps-panel';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-root',
  imports: [CommonModule, Sidebar, MatrixInput, Parameters, StepsPanel],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  selectedMethod = signal<MethodType>('Gauss Elimination');
  numEquations = signal<number>(3);

  matrixA = signal<string[][]>([]);
  vectorB = signal<string[]>([]);
  precision = signal<number>(5);
  mode = signal<'numerical' | 'symbolic'>('numerical');

  solution = signal<string[] | null>(null);
  executionTime = signal(0);
  iterations = signal(0);

  errorHappened = signal<boolean>(false)
  errorMessage = signal<string>("")
  message = signal<string>('');

  num_of_ites_condition = signal<boolean>(true)
  simulationSteps = signal<SimulationStep[]>([]);
  stepDescriptions = signal<string[]>([]);
  xsEquations = signal<string[]>([]);
  ysEquations = signal<string[]>([]);

  isIterativeMethod = computed(() => {
    const m = this.selectedMethod();
    return m === 'Gauss-Seidel' || m === 'Jacobi-Iteration';
  });

  constructor(
    private api: SolverService
  ) { }

  onMatrixDataChange(data: { A: string[][], B: string[], precision: number }) {
    this.matrixA.set(data.A);
    this.vectorB.set(data.B);
    this.precision.set(data.precision);
  }

  // Helper to check for consistency
  checkSystemState(matrix: string[][], rhs: string[]): string | null { // UPDATED: Added consistency check
    // 1. Try parse to numbers
    const n = matrix.length;
    const A: number[][] = [];
    const B: number[] = [];

    for(let i=0; i<n; i++) {
      const row: number[] = [];
      for(let j=0; j<n; j++) {
        const val = parseFloat(matrix[i][j]);
        if(isNaN(val)) return null; // Symbolic mode, skip check
        row.push(val);
      }
      const bVal = parseFloat(rhs[i]);
      if(isNaN(bVal)) return null;
      B.push(bVal);
      A.push(row);
    }

    // 2. Form Augmented Matrix [A | B]
    const aug = A.map((row, i) => [...row, B[i]]);
    const cols = n + 1;

    // 3. Gaussian Elimination to REF
    let pivotRow = 0;
    for (let col = 0; col < n && pivotRow < n; col++) {
      // Find pivot
      let maxRow = pivotRow;
      for (let i = pivotRow + 1; i < n; i++) {
        if (Math.abs(aug[i][col]) > Math.abs(aug[maxRow][col])) {
          maxRow = i;
        }
      }

      if (Math.abs(aug[maxRow][col]) < 1e-9) {
        continue; // Column is zero, move to next col
      }

      // Swap
      [aug[pivotRow], aug[maxRow]] = [aug[maxRow], aug[pivotRow]];

      // Eliminate
      for (let i = pivotRow + 1; i < n; i++) {
        const factor = aug[i][col] / aug[pivotRow][col];
        for (let j = col; j < cols; j++) {
          aug[i][j] -= factor * aug[pivotRow][j];
        }
      }
      pivotRow++;
    }

    // 4. Calculate Ranks
    let rankA = 0;
    let rankAug = 0;

    for (let i = 0; i < n; i++) {
      let rowIsZeroA = true;
      let rowIsZeroAug = true;

      for (let j = 0; j < n; j++) {
        if (Math.abs(aug[i][j]) > 1e-9) {
          rowIsZeroA = false;
          break;
        }
      }

      for (let j = 0; j < cols; j++) {
        if (Math.abs(aug[i][j]) > 1e-9) {
          rowIsZeroAug = false;
          break;
        }
      }

      if (!rowIsZeroA) rankA++;
      if (!rowIsZeroAug) rankAug++;
    }

    // 5. Determine State
    if (rankA < rankAug) {
      return "System is inconsistent (No Solution).";
    }
    if (rankA < n) {
      return "System has infinite number of solutions.";
    }

    return null; // Unique solution
  }

  onSolve(params: SolverParams) {
    // const startTime = performance.now();
    this.errorHappened.set(false)
    this.errorMessage.set('');
    this.solution.set(null);
    this.simulationSteps.set([]);
    this.stepDescriptions.set([]);
    this.xsEquations.set([]);
    this.ysEquations.set([]);
    this.message.set('');

    const consistencyError = this.checkSystemState(this.matrixA(), this.vectorB());
    if (consistencyError) {
      this.errorMessage.set(consistencyError);
      this.errorHappened.set(true);
      return;
    }

    let methodUsed: string = 'GaussElimination'
    switch (this.selectedMethod()) {
      case 'Gauss Elimination':
        methodUsed = 'gauss_elimination'
        break;
      case 'Gauss-Jordan':
        methodUsed = 'gauss_jordan'
        break;
      case 'LU Decomposition':
        switch (params.luForm) {
          case 'Doolittle':
            methodUsed = 'doolittle_lu'
            break;
          case 'Crout':
            methodUsed = 'crout_lu'
            break;
          case 'Cholesky':
            methodUsed = 'cholesky'
            break;
        }
        break;
      case 'Gauss-Seidel':
        methodUsed = 'gauss_seidel'
        break;
      case 'Jacobi-Iteration':
        methodUsed = 'jacobi'
        break;
    }

    // console.log('Solving with:', methodUsed);
    // console.log('Matrix A:', this.matrixA());
    // console.log('Vector B:', this.vectorB());
    // console.log('Precision: ', this.precision());
    // console.log('Params:', params);

    let dataSent: RequestData = {
      A: this.matrixA(),
      b: this.vectorB(),
      mode : this.mode(),
      n : this.numEquations(),
      method: methodUsed,
      precision: this.precision(),
      withScaling: params.useScaling,
      initial_guess: params.initialGuess,
      num_of_ites: params.maxIterations,
      abs_rel_error: params.tolerance
    }

    console.log("DATA TO BE SENT TO BACKEND:")
    console.log(dataSent)

    this.api.getSolution(dataSent).subscribe({
      next: (response: ResponseData) => {
        console.log('Response from Backend: ', response);

        if (!response.solution) {
          this.errorHappened.set(true);
          this.errorMessage.set("No solution returned from backend.");
          return;
        }

        // Handle both numerical and symbolic solutions
        const result = response.solution.map((val) => {
          // If it's a number, format it; if it's a string (symbolic), keep as-is
          if (typeof val === 'number') {
            return val.toPrecision(this.precision());
          } else if (typeof val === 'string') {
            // Check if it's a numeric string
            const numVal = parseFloat(val);
            if (!isNaN(numVal) && isFinite(numVal)) {
              return numVal.toPrecision(this.precision());
            }
            // It's a symbolic expression, return as-is
            return val;
          }
          return String(val);
        });
        this.solution.set(result);

        this.iterations.set((this.selectedMethod() === 'Gauss-Seidel' || this.selectedMethod() === 'Jacobi-Iteration')
          ? response.num_of_ites ?? params.maxIterations : 0);
        // mockSteps = response.steps;
        switch (this.selectedMethod()) {
          case 'Gauss Elimination':
            this.simulationSteps.set(response.steps as DirectStep[])
            break;
          case 'Gauss-Jordan':
            this.simulationSteps.set(response.steps as DirectStep[])
            break;
          case 'LU Decomposition':
            // Backend sends [L, U] arrays, transform to { type: 'lu', L, U } objects
            const luSteps: LUStep[] = response.steps.map((step: any) => ({
              type: 'lu' as const,
              L: step[0],
              U: step[1]
            }));
            this.simulationSteps.set(luSteps);
            break;
          case 'Gauss-Seidel':
            this.simulationSteps.set(response.steps as IterativeStep[])
            break;
          case 'Jacobi-Iteration':
            this.simulationSteps.set(response.steps as IterativeStep[])
            break;
        }
        this.stepDescriptions.set(response.steps_descriptions)
        this.xsEquations.set(response.Xs_steps);
        this.ysEquations.set(response.Ys_steps);
        this.message.set(response.message)

        // const endTime = performance.now();
        this.executionTime.set(parseFloat(response.executionTime.toFixed(12)));
      },
      error: (error: HttpErrorResponse) => {
        console.log("ERROR")
        console.log(error)
        console.error('Error Sending Solution Request:', error.error.error);
        this.errorHappened.set(true)
        this.solution.set([])
        this.errorMessage.set(error.error.error)
      }
    })
  }
}
