import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RootFinder } from './root-finder';

describe('RootFinder', () => {
  let component: RootFinder;
  let fixture: ComponentFixture<RootFinder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RootFinder]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RootFinder);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
