import { Component, EventEmitter, Input, Output, signal, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-matrix-input',
  imports: [FormsModule],
  templateUrl: './matrix-input.html',
  styleUrl: './matrix-input.css',
})
export class MatrixInput {
  @Input() size: number = 3;
  @Output() sizeChange = new EventEmitter<number>();
  @Output() matrixChange = new EventEmitter<{ A: string[][], B: string[], precision: number }>();
  @Output() modeChange = new EventEmitter<'numerical' | 'symbolic'>();

  precision = signal(4);
  matrix = signal<string[][]>([]);
  rhs = signal<string[]>([]);

  ngOnChanges(changes: SimpleChanges) {
    if (changes['size']) {
      this.regenerateMatrix(this.size);
    }
  }

  regenerateMatrix(n: number) {
    if (n < 2) return;

    // Use current values to preserve data when resizing
    const currentMatrix = this.matrix();
    const currentRhs = this.rhs();

    const newMatrix: string[][] = Array(n).fill(0).map((_, i) =>
      Array(n).fill(0).map((_, j) => (currentMatrix[i] && currentMatrix[i][j]) || "0")
    );
    const newRhs: string[] = Array(n).fill(0).map((_, i) => currentRhs[i] || "0");

    this.matrix.set(newMatrix);
    this.rhs.set(newRhs);
    this.emitChanges();
  }

  onSizeChange(val: number) {
    this.sizeChange.emit(val);
  }

  onPrecisionChange(val: number) {
    this.precision.set(val);
    this.emitChanges();
  }

  updateMatrixCell(i: number, j: number, val: string) {
    this.matrix.update(m => {
      const row = [...m[i]];
      row[j] = val;
      const newM = [...m];
      newM[i] = row;
      return newM;
    });
    this.emitChanges();
  }

  updateRhsCell(i: number, val: string) {
    this.rhs.update(v => {
      const newV = [...v];
      newV[i] = val;
      return newV;
    });
    this.emitChanges();
  }

  emitChanges() {
    // Detect Mode more robustly
    let hasSymbol = false;

    // Check Matrix A
    const currentMatrix = this.matrix();
    console.log("currentMatrix:")
    console.log(currentMatrix)
    for (const row of currentMatrix) {
      for (const val of row) {
        if (this.isSymbolic(val)) {
          hasSymbol = true;
          break;
        }
      }
      if (hasSymbol) break;
    }

    // Check Vector B if still not found
    if (!hasSymbol) {
      const currentRhs = this.rhs();
      for (const val of currentRhs) {
        if (this.isSymbolic(val)) {
          hasSymbol = true;
          break;
        }
      }
    }

    const detectedMode = hasSymbol ? 'symbolic' : 'numerical';
    this.modeChange.emit(detectedMode);

    this.matrixChange.emit({
      A: this.matrix(),
      B: this.rhs(),
      precision: this.precision()
    });
  }

  // Helper to determine if a value is symbolic (not a valid number)
  private isSymbolic(val: string): boolean {
    if (!val) return false;
    const v = val.toString().trim();
    if (v === '') return false; // Treat empty string as 0 (numerical)
    // If it's NOT a number, it's symbolic (e.g. "a", "1/2", "2*x")
    return isNaN(Number(v));
  }

  isValid(expr: string): boolean { 
    if (!expr || expr.trim() === '') return false; 
    const validChars = /^[a-zA-Z0-9\s+\-*/^()._]+$/; 
    const endsWithOperator = /[+\-*/^]$/; 
    return validChars.test(expr) && !endsWithOperator.test(expr.trim()); 
  }
}
