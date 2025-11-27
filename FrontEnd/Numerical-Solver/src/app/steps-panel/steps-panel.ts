import { Component, computed, Input, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'steps-panel',
  standalone: true,
  templateUrl: './steps-panel.html',
  imports: [
    DecimalPipe
  ],
  styleUrls: ['./steps-panel.css']
})
export class StepsPanel {
  @Input({ required: true }) steps: SimulationStep[] = [];
  @Input({ required: true }) isIterative!: boolean;

  currentIndex = signal(0);

  currentDirectStep = computed(() => {
    return this.steps[this.currentIndex()] as DirectStep;
  });

  currentIterativeStep = computed(() => {
    return this.steps[this.currentIndex()] as IterativeStep;
  });

  nextStep() {
    if (this.currentIndex() < this.steps.length - 1) {
      this.currentIndex.update(i => i + 1);
    }
  }

  prevStep() {
    if (this.currentIndex() > 0) {
      this.currentIndex.update(i => i - 1);
    }
  }
}
