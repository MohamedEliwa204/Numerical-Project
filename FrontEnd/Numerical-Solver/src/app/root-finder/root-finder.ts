import { Component, Input, OnInit, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SolverService } from '../services/solver-service';
// @ts-ignore
import Plotly from 'plotly.js-dist-min';

@Component({
  selector: 'app-root-finder',
  standalone: true,
  imports: [CommonModule, FormsModule],
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

  // State
  isLoading = signal<boolean>(false);
  errorMessage = signal<string>('');
  result = signal<any>(null);
  plotData = signal<any>(null);

  constructor(private api: SolverService) {
    // Reset inputs when method changes
    effect(() => {
      this.method; // dependency
      this.result.set(null);
      this.errorMessage.set('');
      this.plotData.set(null);
    });
  }

  ngOnInit() {}

  get isBracketing(): boolean {
    return ['Bisection', 'False-Position'].includes(this.method);
  }

  get isOpenMethod(): boolean {
    return !this.isBracketing;
  }
  
  get isSecant(): boolean {
    return this.method === 'Secant Method';
  }

  async onPlot() {
    if (!this.equation()) {
      this.errorMessage.set('Please enter an equation.');
      return;
    }
    
    this.isLoading.set(true);
    this.errorMessage.set('');
    
    try {
      // Assuming backend has a plot endpoint that returns Plotly JSON
      const response = await this.api.getFunctionPlot({
        function: this.equation(),
        method: this.method
      }).toPromise();
      
      this.plotData.set(response);
      this.renderPlot(response.data, response.layout);
    } catch (err: any) {
      this.errorMessage.set(err.error?.error || 'Failed to plot function');
    } finally {
      this.isLoading.set(false);
    }
  }

  renderPlot(data: any[], layout: any) {
    const plotDiv = document.getElementById('function-plot');
    if (plotDiv) {
      Plotly.newPlot(plotDiv, data, layout, { responsive: true }); // the line responsible for the plotting
    }
  }

  async onSolve() {
    if (!this.equation()) {
      this.errorMessage.set('Please enter an equation.');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.result.set(null);

    const payload: any = {
      method: this.method,
      function: this.equation(),
      precision: this.precision(),
      max_iterations: this.maxIterations(),
      epsilon: this.epsilon()
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

    try {
      const response = await this.api.solveRoot(payload).toPromise();
      this.result.set(response);
    } catch (err: any) {
      this.errorMessage.set(err.error?.error || 'Failed to find root');
    } finally {
      this.isLoading.set(false);
    }
  }
}