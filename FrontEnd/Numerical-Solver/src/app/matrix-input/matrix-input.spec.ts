import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatrixInput } from './matrix-input';

describe('MatrixInput', () => {
  let component: MatrixInput;
  let fixture: ComponentFixture<MatrixInput>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatrixInput]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MatrixInput);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
