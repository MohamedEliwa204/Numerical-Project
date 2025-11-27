type MethodType = 'Gauss Elimination' | 'Gauss-Jordan' | 'LU Decomposition' | 'Gauss-Seidel' | 'Jacobi-Iteration';
type LUForm = 'Doolittle' | 'Crout' | 'Cholesky';
type StopCondition = 'Number of Iterations' | 'Absolute Relative Error';
// Step types based on user description
// Direct: [Matrix(2D), Vector(1D)]
// Iterative: [Solution(1D), Errors(1D)]
type DirectStep = [number[][], number[]];
type IterativeStep = [number[], number[]];
type SimulationStep = DirectStep | IterativeStep;

interface SolverParams {
  initialGuess: number[];
  tolerance: number;
  maxIterations: number;
  luForm: LUForm;
  useScaling: boolean;
}
