import { CommonModule } from '@angular/common';
import { Component, SimpleChanges, EventEmitter, Input, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-parameters',
  imports: [CommonModule, FormsModule],
  templateUrl: './parameters.html',
  styleUrl: './parameters.css',
})
export class Parameters {
  @Input({ required: true }) method!: MethodType;
  @Input({ required: true }) size!: number;
  @Output() solve = new EventEmitter<SolverParams>();

  initialGuess = signal<number[]>([]);
  tolerance = signal(0.0001);
  maxIterations = signal(50);
  luForm = signal<LUForm>('Doolittle');
  stopCondition = signal<StopCondition>('Number of Iterations');
  useScaling = signal(false); // New signal for scaling option

  get isIterative(): boolean {
    return this.method === 'Gauss-Seidel' || this.method === 'Jacobi-Iteration';
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['size']) {
      this.initialGuess.update(prev => {
        if (prev.length === this.size) return prev;
        return new Array(this.size).fill(0);
      });
    }
  }

  updateGuess(index: number, val: number) {
    this.initialGuess.update(arr => {
      const newArr = [...arr];
      newArr[index] = val;
      return newArr;
    });
  }

  emitSolve() {
    this.solve.emit({
      initialGuess: this.initialGuess(),
      tolerance: this.tolerance(),
      maxIterations: this.maxIterations(),
      luForm: this.luForm(),
      useScaling: this.useScaling()
    });
  }
}
