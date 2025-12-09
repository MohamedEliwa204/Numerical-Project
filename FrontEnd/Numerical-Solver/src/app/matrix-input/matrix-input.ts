import { Component, EventEmitter, Input, Output, signal, SimpleChanges, OnInit } from '@angular/core';
import { FormsModule, FormControl, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-matrix-input',
  imports: [FormsModule, ReactiveFormsModule],
  templateUrl: './matrix-input.html',
  styleUrl: './matrix-input.css',
})
export class MatrixInput implements OnInit {
  @Input() size: number = 3;
  @Output() sizeChange = new EventEmitter<number>();
  @Output() matrixChange = new EventEmitter<{ A: string[][], B: string[], precision: number }>();
  @Output() modeChange = new EventEmitter<'numerical' | 'symbolic'>();

  // precision = signal(5);
  precision = new FormControl<number>(5, {nonNullable : true})
  nativeSize = new FormControl<number>(3, {nonNullable : true})
  constructor() {
    this.precision.valueChanges.subscribe(value => {
      this.onPrecisionChange(value)
    })
    this.nativeSize.valueChanges.subscribe(val => {
      const validated = this.onSizeChange(val)
      if (val !== validated) {
        this.nativeSize.setValue(validated, { emitEvent: false })
      }
      this.regenerateMatrix(validated)
    })
  }

  ngOnInit() {
    this.nativeSize.setValue(this.size, {emitEvent: false});
    this.regenerateMatrix(this.size);
  }
  
  minPrecision = 1
  maxPrecision = 15
  matrix = signal<string[][]>([]);
  minSize = 2
  maxSize = 50
  rhs = signal<string[]>([]);

  // ngOnChanges(changes: SimpleChanges) {
  //   if (changes['size']) {
  //     this.regenerateMatrix(this.size);
  //   }
  // }

  regenerateMatrix(n: number) {
    if (n < 2) return;

    // Use current values to preserve data when resizing
    const currentMatrix = this.matrix();
    const currentRhs = this.rhs();

    const newMatrix: string[][] = Array(n).fill(0).map((_, i) =>
      Array(n).fill(0).map((_, j) => {
        // Check if the row exists and the cell exists
        if (currentMatrix[i] && currentMatrix[i][j] !== undefined && currentMatrix[i][j] !== null) {
          return currentMatrix[i][j];
        }
        return "0";
      })
    );
    const newRhs: string[] = Array(n).fill(0).map((_, i) => {
      if (currentRhs[i] !== undefined && currentRhs[i] !== null) {
        return currentRhs[i];
      }
      return "0";
    });

    this.matrix.set(newMatrix);
    this.rhs.set(newRhs);
    this.emitChanges();
  }

  onSizeChange(val: any): number {
    // Parse to number, default to minSize if invalid
    let numVal = parseInt(val, 10);
    
    // If not a valid number, set to minimum
    if (isNaN(numVal) || !isFinite(numVal)) {
      numVal = this.minSize;
    }
    
    // Clamp between min and max
    if (numVal > this.maxSize) {
      numVal = this.maxSize;
    } else if (numVal < this.minSize) {
      numVal = this.minSize;
    }
    
    this.size = numVal;
    this.sizeChange.emit(numVal);
    return numVal;
  }

  onPrecisionChange(val: any) {
    // Parse to number, default to minPrecision if invalid
    let numVal = parseInt(val, 10);

    // If not a valid number, set to minimum
    if (isNaN(numVal) || !isFinite(numVal)) {
      numVal = this.minPrecision;
    }
    
    // Clamp between min and max
    if (numVal > this.maxPrecision) {
      numVal = this.maxPrecision;
    } else if (numVal < this.minPrecision) {
      numVal = this.minPrecision;
    }
    
    this.precision.setValue(numVal);
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
      precision: this.precision.value
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
