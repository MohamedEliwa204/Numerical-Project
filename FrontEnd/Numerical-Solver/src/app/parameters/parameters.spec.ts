import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Parameters } from './parameters';

describe('Parameters', () => {
  let component: Parameters;
  let fixture: ComponentFixture<Parameters>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Parameters]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Parameters);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
