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

  @Output() num_of_ites_condition = new EventEmitter<boolean>();

  initialGuess = signal<string[]>([]);
  tolerance = signal(0.0001);
  maxIterations = 200;  // Changed to regular property (constant limit)
  minIterations = 1;    // Changed to regular property (constant limit)
  iterationsNum = signal(20);
  luForm = signal<LUForm>('Doolittle');
  stopCondition = signal<StopCondition>('Number of Iterations');
  useScaling = signal(false);

  get isIterative(): boolean {
    return this.method === 'Gauss-Seidel' || this.method === 'Jacobi-Iteration';
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['size']) {
      this.initialGuess.update(prev => {
        if (prev.length === this.size) return prev;
        return new Array(this.size).fill("0");
      });
    }

    if (this.stopCondition() === 'Number of Iterations')
      this.num_of_ites_condition.emit(true)
    else
      this.num_of_ites_condition.emit(false)
  }

  updateGuess(index: number, val: string) {
    this.initialGuess.update(arr => {
      const newArr = [...arr];
      newArr[index] = val;
      return newArr;
    });
  }

  onIterationsChange(val: any) {
    // Parse to number, default to minIterations if invalid
    let numVal = parseInt(val, 10);
    
    // If not a valid number, set to minimum
    if (isNaN(numVal) || !isFinite(numVal)) {
      numVal = this.minIterations;
    }
    
    // Clamp between min and max
    if (numVal > this.maxIterations) {
      numVal = this.maxIterations;
    } else if (numVal < this.minIterations) {
      numVal = this.minIterations;
    }
    
    this.iterationsNum.set(numVal);
  }

  emitSolve() {
    this.solve.emit({
      initialGuess: this.initialGuess(),
      tolerance: this.tolerance(),
      maxIterations: this.iterationsNum(),  // Use iterationsNum instead of maxIterations
      luForm: this.luForm(),
      useScaling: this.useScaling()
    });
  }
}
