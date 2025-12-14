import { Component, Input, OnInit, signal, effect } from '@angular/core';
import { CommonModule, KeyValuePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SolverService } from '../services/solver-service';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';

@Component({
  selector: 'app-root-finder',
  standalone: true,
  imports: [CommonModule, FormsModule, KeyValuePipe],
  templateUrl: './root-finder.html',
  styleUrl: './root-finder.css'
})
export class RootFinder implements OnInit {
  @Input({ required: true }) method!: string;

  // Parameters
  equation = signal<string>('');
  precision = signal<number>(10);
  maxIterations = signal<number>(50);
  epsilon = signal<number>(0.00001);

  // Method specific params
  xl = signal<number>(0);
  xu = signal<number>(1);
  x0 = signal<number>(0);
  x1 = signal<number>(1); // For Secant
  gx = signal<string>(''); // For Fixed Point - g(x) function
  gxTouched = signal<boolean>(false); // Track if user has interacted with g(x)

  // State
  isLoading = signal<boolean>(false);
  errorMessage = signal<string>('');
  result = signal<any>(null);
  plotData = signal<any>(null);

  // Base plot data (the main function curve)
  basePlotData = signal<any[]>([]);
  basePlotLayout = signal<any>(null);

  // Step navigation
  currentStepIndex = signal<number>(0);
  showStepsTable = signal<boolean>(false);

  toggleStepsTable() {
    this.showStepsTable.update(v => !v);
  }

  constructor(private api: SolverService) {
    // Reset inputs when method changes
    effect(() => {
      this.method; // dependency
      this.result.set(null);
      this.errorMessage.set('');
      this.plotData.set(null);
      this.basePlotData.set([]);
      this.basePlotLayout.set(null);
      this.currentStepIndex.set(0);
      this.gxTouched.set(false);
    });
  }

  ngOnInit() { }

  get isBracketing(): boolean {
    return ['Bisection', 'False-Position'].includes(this.method);
  }

  get isOpenMethod(): boolean {
    return !this.isBracketing;
  }

  get isSecant(): boolean {
    return this.method === 'Secant Method';
  }

  get isFixedPoint(): boolean {
    return this.method === 'Fixed Point';
  }

  get canSolve(): boolean {
    // Must have equation
    if (!this.equation()) return false;
    // If Fixed Point, must have g(x)
    if (this.isFixedPoint && !this.gx().trim()) return false;
    return true;
  }

  get canPlot(): boolean {
    // Must have equation
    return this.equation().trim().length > 0;
  }

  get gxError(): string {
    if (this.isFixedPoint && this.gxTouched() && !this.gx().trim()) {
      return 'g(x) function is required for Fixed Point method';
    }
    return '';
  }

  // Generate the y=x line trace for Fixed Point method
  private getYEqualsXTrace(): any {
    const xMin = -10;
    const xMax = 10;
    const xValues = [];
    const yValues = [];
    const step = 0.1;

    for (let x = xMin; x <= xMax; x += step) {
      xValues.push(x);
      yValues.push(x); // y = x
    }

    return {
      x: xValues,
      y: yValues,
      type: 'scatter',
      mode: 'lines',
      name: 'y = x',
      line: { color: '#ff6b6b', width: 2, dash: 'solid' }
    };
  }

  onPlot() {
    if (!this.equation()) {
      this.errorMessage.set('Please enter an equation.');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');

    // Assuming backend has a plot endpoint that returns Plotly JSON
    this.api.getFunctionPlot({
      func: this.equation().toLowerCase(),
      method: (this.method == "Fixed Point") ? "fixed_point" : undefined
    }).subscribe({
      next: (response) => {
        this.plotData.set(response);

        // Add y=x line for Fixed Point method
        let plotDataWithExtras = [...response.data];
        // if (this.isFixedPoint) {
        //   plotDataWithExtras.push(this.getYEqualsXTrace());
        // }

        // Store the base plot data (including y=x for fixed point) and layout
        this.basePlotData.set(plotDataWithExtras);
        this.basePlotLayout.set(response.layout);
        this.renderPlot(plotDataWithExtras, response.layout);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.error || 'Failed to plot function');
        this.isLoading.set(false);
      }
    });
  }

  renderPlot(data: any[], layout: any) {
    const plotDiv = document.getElementById('function-plot');
    if (plotDiv) {
      Plotly.newPlot(plotDiv, data, layout, { responsive: true });
    }
  }

  // Overlay step traces on the base plot
  renderStepOnPlot(stepIndex: number) {
    const result = this.result();
    if (!result || !result.steps || stepIndex >= result.steps.length) return;

    const step = result.steps[stepIndex];
    const baseData = this.basePlotData();
    const baseLayout = this.basePlotLayout();

    if (!baseData || baseData.length === 0) return;

    // Combine base plot data with step traces
    if (this.isFixedPoint) {
      const combinedData = [ ...(step.plot_data || [])];
      this.renderPlot(combinedData, baseLayout);
    }
    else {
      const combinedData = [...baseData, ...(step.plot_data || [])];
      this.renderPlot(combinedData, baseLayout);
    }
  }

  // Step navigation methods
  nextStep() {
    const result = this.result();
    if (result && result.steps && this.currentStepIndex() < result.steps.length - 1) {
      this.currentStepIndex.update(i => i + 1);
      this.renderStepOnPlot(this.currentStepIndex());
    }
  }

  prevStep() {
    if (this.currentStepIndex() > 0) {
      this.currentStepIndex.update(i => i - 1);
      this.renderStepOnPlot(this.currentStepIndex());
    }
  }

  goToStep(index: number) {
    const result = this.result();
    if (result && result.steps && index >= 0 && index < result.steps.length) {
      this.currentStepIndex.set(index);
      this.renderStepOnPlot(index);
    }
  }

  // Get current step data
  get currentStep(): any {
    const result = this.result();
    if (!result || !result.steps || result.steps.length === 0) return null;
    return result.steps[this.currentStepIndex()];
  }

  // Get dynamic table headers from the first step's numericals keys
  get tableHeaders(): string[] {
    const result = this.result();
    if (!result || !result.steps || result.steps.length === 0) return [];
    const firstStep = result.steps[0];
    if (!firstStep.numericals) return [];
    return Object.keys(firstStep.numericals);
  }

  // Beautify backend error messages for user-friendly display
  private beautifyErrorMessage(rawMessage: any): string {
    // Handle non-string inputs
    if (!rawMessage) return 'An unknown error occurred.';
    if (typeof rawMessage !== 'string') {
      // If it's an object, try to extract a message
      if (typeof rawMessage === 'object') {
        rawMessage = rawMessage.message || rawMessage.error || JSON.stringify(rawMessage);
      } else {
        rawMessage = String(rawMessage);
      }
    }

    const msg = rawMessage.toLowerCase();

    // Complex number errors (e.g., taking sqrt of negative)
    if (msg.includes('complex') || msg.includes('not a real number')) {
      return 'The function produces complex (imaginary) numbers at the given initial value. Try a different starting point where the function remains real-valued.';
    }

    // Overflow / Infinity errors
    if (msg.includes('infinity') || msg.includes('overflow') || msg.includes('too large')) {
      return 'The method diverged to infinity. The function may not converge with the given parameters. Try a different initial guess or check your function.';
    }

    // Division by zero
    if (msg.includes('division by zero') || msg.includes('divide by zero')) {
      return 'Division by zero encountered. The derivative may be zero at some point. Try a different initial guess.';
    }

    // NaN errors
    if (msg.includes('nan') || msg.includes('not a number')) {
      return 'The calculation resulted in an undefined value. Check your function and initial parameters.';
    }

    // Convergence failures
    if (msg.includes('diverge') || msg.includes('does not converge')) {
      return 'The method did not converge. Try adjusting the initial guess or check if the function has a root in the expected region.';
    }

    // Bracket errors
    if (msg.includes('bracket') || msg.includes('not bracketed')) {
      return 'The root is not bracketed between the given bounds. Ensure f(xl) and f(xu) have opposite signs. May have discontinuity or even roots';
    }

    // Parse errors
    if (msg.includes('parse') || msg.includes('syntax')) {
      return 'Could not parse the function. Please check the syntax of your equation.';
    }

    // Default: return a cleaned-up version
    return rawMessage.replace(/^Math Error[^:]*:\s*/i, '').trim() || 'An error occurred during calculation.';
  }

  onSolve() {
    if (!this.equation()) {
      this.errorMessage.set('Please enter an equation.');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.result.set(null);



    let payload: any = {
      func: (this.isFixedPoint) ? this.gx().toLowerCase() : this.equation().toLowerCase(),
      precision: this.precision(),
      max_iter: this.maxIterations(),
      tolerance: this.epsilon()
    };

    if (this.isBracketing) {
      payload.xl = this.xl();
      payload.xu = this.xu();
    } else {
      payload.x0 = this.x0();
      if (this.isSecant) {
        payload.x1 = this.x1();
      }
    }

    // Map display method name to backend method name
    let backendMethod = '';
    switch (this.method) {
      case "Bisection":
        backendMethod = "bisection";
        break;
      case "False-Position":
        backendMethod = "false_position";
        break;
      case "Fixed Point":
        backendMethod = "fixed_point";
        break;
      case "Original Newton-Raphson":
        backendMethod = "newton_raphson";
        break;
      case "Modified Newton-Raphson":
        backendMethod = "modified_newton_raphson";
        break;
      case "Secant Method":
        backendMethod = "secant_method";
        break;
      default:
        backendMethod = this.method.toLowerCase().replace(/-/g, '_');
    }

    payload.method = backendMethod;

    this.api.solveRoot(payload).subscribe({
      next: (response) => {
        this.result.set(response);
        console.log(response)
        this.currentStepIndex.set(0);

        // If the response has an error status, beautify the message
        if (response.status === 'error' && response.message) {
          response.message = this.beautifyErrorMessage(response.message);
          this.result.set(response);
        }

        // If we have steps and base plot, render the first step
        if (response.steps && response.steps.length > 0 && this.basePlotData().length > 0) {
          this.renderStepOnPlot(0);
        }
        this.isLoading.set(false);
      },
      error: (err) => {
        console.log(err)
        const rawError = err.error?.error || err.error?.message || 'Failed to find root';
        this.errorMessage.set(this.beautifyErrorMessage(rawError));
        this.isLoading.set(false);
      }
    });
  }
}