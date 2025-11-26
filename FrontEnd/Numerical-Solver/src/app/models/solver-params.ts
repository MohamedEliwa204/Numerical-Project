type MethodType = 'Gauss Elimination' | 'Gauss-Jordan' | 'LU Decomposition' | 'Gauss-Seidel' | 'Jacobi-Iteration';
type LUForm = 'Doolittle' | 'Crout' | 'Cholesky';
type StopCondition = 'Number of Iterations' | 'Absolute Relative Error';

interface SolverParams {
  initialGuess: number[];
  tolerance: number;
  maxIterations: number;
  luForm: LUForm;
  useScaling: boolean;
}