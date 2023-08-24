import { ComponentFixture, TestBed } from '@angular/core/testing'

import { ContentReduceViewComponent } from './content-reduce-view.component'

describe('ContentReduceViewComponent', () => {
  let component: ContentReduceViewComponent
  let fixture: ComponentFixture<ContentReduceViewComponent>

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ContentReduceViewComponent],
    }).compileComponents()

    fixture = TestBed.createComponent(ContentReduceViewComponent)
    component = fixture.componentInstance
    fixture.detectChanges()
  })

  it('should create', () => {
    expect(component).toBeTruthy()
  })
})
