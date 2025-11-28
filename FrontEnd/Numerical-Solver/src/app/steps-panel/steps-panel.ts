import { Component, computed, Input, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'steps-panel',
  standalone: true,
  templateUrl: './steps-panel.html',
  imports: [],
  styleUrls: ['./steps-panel.css']
})
export class StepsPanel {
  @Input({ required: true }) steps: SimulationStep[] = [];
  @Input() descriptions: string[] = [];
  @Input() xsEquations: string[] = [];
  @Input() ysEquations: string[] = [];
  @Input({ required: true }) isIterative!: boolean;

  currentIndex = signal(0);

  allSteps = computed(() => {
    const list: SimulationStep[] = [...this.steps];

    if (this.ysEquations && this.ysEquations.length > 0) {
      list.push({
        type: 'eq',
        title: 'Forward Substitution (L.Y = B)',
        equations: this.ysEquations
      });
    }

    if (this.xsEquations && this.xsEquations.length > 0) {
      list.push({
        type: 'eq',
        title: 'Backward Substitution ' + (this.ysEquations.length > 0 ? '(U.X = Y)' : ''),
        equations: this.xsEquations
      });
    }

    return list;
  });

  currentStep = computed(() => this.allSteps()[this.currentIndex()]);

  currentDirectStep = computed(() => {
    return this.steps[this.currentIndex()] as DirectStep;
  });

  currentIterativeStep = computed(() => {
    return this.steps[this.currentIndex()] as IterativeStep;
  });

  // Type Guards
  isLUStep(step: SimulationStep): boolean {
    return 'type' in step && step.type === 'lu';
  }
  
  isEquationStep(step: SimulationStep): boolean {
    return 'type' in step && step.type === 'eq';
  }

  // Type Casters
  asDirectStep(step: SimulationStep): DirectStep { return step as DirectStep; }
  asIterativeStep(step: SimulationStep): IterativeStep { return step as IterativeStep; }
  asLUStep(step: SimulationStep): LUStep { return step as LUStep; }
  asEquationStep(step: SimulationStep): EquationStep { return step as EquationStep; }

  nextStep() {
    if (this.currentIndex() < this.allSteps().length - 1) {
      this.currentIndex.update(i => i + 1);
    }
  }

  prevStep() {
    if (this.currentIndex() > 0) {
      this.currentIndex.update(i => i - 1);
    }
  }

  parseEquation(eqStr: string) {
    const regex = /^([XY]\d+)\s*=\s*\((.*)\)\s*\/\s*([^\s=]+)\s*=\s*(.*)$/;
    const match = eqStr.match(regex);
    
    if (match) {
      return {
        variable: match[1],
        numerator: match[2],
        denominator: match[3],
        result: match[4]
      };
    }
    return null;
  }

  parseMathParts(text: string) {
    const parts: { text: string; isVar: boolean; base?: string; sub?: string }[] = [];
    const regex = /([XYR])(\d+)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      // Push text before match
      if (match.index > lastIndex) {
        parts.push({ text: text.substring(lastIndex, match.index), isVar: false });
      }
      // Push match
      parts.push({ text: match[0], isVar: true, base: match[1], sub: match[2] });
      lastIndex = regex.lastIndex;
    }
    // Push remaining text
    if (lastIndex < text.length) {
      parts.push({ text: text.substring(lastIndex), isVar: false });
    }
    return parts;
  }
}
