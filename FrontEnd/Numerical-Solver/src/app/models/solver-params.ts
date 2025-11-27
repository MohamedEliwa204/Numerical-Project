type MethodType = 'Gauss Elimination' | 'Gauss-Jordan' | 'LU Decomposition' | 'Gauss-Seidel' | 'Jacobi-Iteration';
type LUForm = 'Doolittle' | 'Crout' | 'Cholesky';
type StopCondition = 'Number of Iterations' | 'Absolute Relative Error';

// Step types based on user description
// Direct: [Matrix(2D), Vector(1D)]
// Iterative: [Solution(1D), Errors(1D)]

type DirectStep = [string[][], string[]];
type IterativeStep = [string[], string[]];
type LUStep = { type: 'lu', L: string[][], U: string[][] };
type EquationStep = { type: 'eq', equations: string[], title: string };
type SimulationStep = DirectStep | IterativeStep | LUStep | EquationStep;

interface SolverParams {
  initialGuess: string[]; // UPDATED
  tolerance: number;
  maxIterations: number;
  luForm: LUForm;
  useScaling: boolean;
}
