import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-sidebar',
  imports: [],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class Sidebar {
  // New Signal Input API
  @Input({ required: true }) selectedMethod!: MethodType;
  @Output() selectMethod = new EventEmitter<MethodType>();

  methods: MethodType[] = [
    'Gauss Elimination',
    'Gauss-Jordan',
    'LU Decomposition',
    'Jacobi-Iteration',
    'Gauss-Seidel'
  ];
}
