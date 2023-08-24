import { ComponentFixture, TestBed } from '@angular/core/testing'

import { ProgramDetailsComponent } from './program-details.component'

describe('ProgramDetailsComponent', () => {
  let component: ProgramDetailsComponent
  let fixture: ComponentFixture<ProgramDetailsComponent>

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ProgramDetailsComponent],
    }).compileComponents()

    fixture = TestBed.createComponent(ProgramDetailsComponent)
    component = fixture.componentInstance
    fixture.detectChanges()
  })

  it('should create', () => {
    expect(component).toBeTruthy()
  })
})
