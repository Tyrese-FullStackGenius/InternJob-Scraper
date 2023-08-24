import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InterestTableComponent } from './interest-table.component';

describe('InterestTableComponent', () => {
  let component: InterestTableComponent;
  let fixture: ComponentFixture<InterestTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InterestTableComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InterestTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
