import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StepsPanel } from './steps-panel';

describe('StepsPanel', () => {
  let component: StepsPanel;
  let fixture: ComponentFixture<StepsPanel>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StepsPanel]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StepsPanel);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
