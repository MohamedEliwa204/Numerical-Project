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
  @Output() matrixChange = new EventEmitter<{ A: number[][], B: number[], precision: number }>();

  precision = signal(4);
  matrix = signal<number[][]>([]);
  rhs = signal<number[]>([]);

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

    const newMatrix: number[][] = Array(n).fill(0).map((_, i) =>
      Array(n).fill(0).map((_, j) => (currentMatrix[i] && currentMatrix[i][j]) || 0)
    );
    const newRhs: number[] = Array(n).fill(0).map((_, i) => currentRhs[i] || 0);

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

  updateMatrixCell(i: number, j: number, val: number) {
    this.matrix.update(m => {
      const row = [...m[i]];
      row[j] = val;
      const newM = [...m];
      newM[i] = row;
      return newM;
    });
    this.emitChanges();
  }

  updateRhsCell(i: number, val: number) {
    this.rhs.update(v => {
      const newV = [...v];
      newV[i] = val;
      return newV;
    });
    this.emitChanges();
  }

  emitChanges() {
    this.matrixChange.emit({
      A: this.matrix(),
      B: this.rhs(),
      precision: this.precision()
    });
  }
}
