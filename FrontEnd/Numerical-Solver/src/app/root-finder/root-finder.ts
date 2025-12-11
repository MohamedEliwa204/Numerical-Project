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
    if (!this.equation().trim()) return false;
    // If Fixed Point, must also have g(x)
    if (this.isFixedPoint && !this.gx().trim()) return false;
    return true;
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
      func: this.equation(),
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
    const combinedData = [...baseData, ...(step.plot_data || [])];
    
    this.renderPlot(combinedData, baseLayout);
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
        // If we have steps and base plot, render the first step
        if (response.steps && response.steps.length > 0 && this.basePlotData().length > 0) {
          this.renderStepOnPlot(0);
        }
        this.isLoading.set(false);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.error || 'Failed to find root');
        this.isLoading.set(false);
      }
    });
  }
}