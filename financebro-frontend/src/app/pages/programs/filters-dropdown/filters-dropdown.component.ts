import { Component, ElementRef, Inject, OnDestroy, OnInit } from '@angular/core'
import { MatDialogConfig, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog'
import { ActivatedRoute, Params, Router } from '@angular/router'
import { Store } from '@ngrx/store'
import * as fromApp from '@store/app.reducer'
import { Dictionary } from '@models/program'
import { Subscription } from 'rxjs'
import { programsFeatureKey } from '@pages/programs/store/programs.reducer'
import { map } from 'rxjs/operators'
import { AvailableFilters } from '@models/program'
import { ProgramsActions } from '@pages/programs/store/programs.actions'

@Component({
  selector: 'app-program-filters',
  templateUrl: './filters-dropdown.component.html',
})
export class FiltersDropdownDialogComponent implements OnInit, OnDestroy {
  private positionRelativeToElement: ElementRef

  urlParamsSubscription: Subscription
  programsSubscription: Subscription
  availableFilters: AvailableFilters
  appliedFilters: Dictionary<string | null> = {
    company_category: null,
    company: null,
    country: null,
    program_category: null,
    region: null,
    is_application_open: null,
    does_ask_for_cover_letter: null,
  }

  constructor(
    private readonly store: Store<fromApp.AppState>,
    public filtersDropdownDialogRef: MatDialogRef<FiltersDropdownDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public options: { positionRelativeToElement: ElementRef },
    private router: Router,
    private activatedRoute: ActivatedRoute,
  ) {
    this.positionRelativeToElement = options.positionRelativeToElement
  }

  ngOnInit(): void {
    this.setupProgramsSubscription()
    this.setupUrlParamsSubscription()
    const matDialogConfig = new MatDialogConfig()
    const rect: DOMRect = this.positionRelativeToElement.nativeElement.getBoundingClientRect()

    matDialogConfig.position = { right: `40px`, top: `${rect.bottom + 2}px` }
    this.filtersDropdownDialogRef.updatePosition(matDialogConfig.position)
  }

  private setupProgramsSubscription() {
    this.programsSubscription = this.store
      .select(programsFeatureKey)
      .pipe(map(programsState => programsState.availableFilters))
      .subscribe(({ filters }) => {
        this.availableFilters = filters
      })
  }

  setupUrlParamsSubscription() {
    this.urlParamsSubscription = this.activatedRoute.queryParamMap.subscribe(params => {
      this.appliedFilters.company_category = params.get('company_category')
      this.appliedFilters.company = params.get('company_id')
      this.appliedFilters.country = params.get('countries')
      this.appliedFilters.program_category = params.get('program_category')
      this.appliedFilters.region = params.get('region')
      this.appliedFilters.is_application_open = params.get('is_application_open') ?? 'True'
      this.appliedFilters.does_ask_for_cover_letter = params.get('does_ask_for_cover_letter')
    })
  }

  applyFilters() {
    let programFilters: Params = {}

    if (this.appliedFilters.company_category) programFilters['company_category'] = this.appliedFilters.company_category
    if (this.appliedFilters.company) programFilters['company_id'] = this.appliedFilters.company
    if (this.appliedFilters.country) programFilters['countries'] = this.appliedFilters.country
    if (this.appliedFilters.program_category) programFilters['program_category'] = this.appliedFilters.program_category
    if (this.appliedFilters.region) programFilters['region'] = this.appliedFilters.region
    if (this.appliedFilters.is_application_open !== null)
      programFilters['is_application_open'] = this.appliedFilters.is_application_open
    if (this.appliedFilters.does_ask_for_cover_letter !== null)
      programFilters['does_ask_for_cover_letter'] = this.appliedFilters.does_ask_for_cover_letter

    this.store.dispatch(ProgramsActions.getAllPrograms({ filters: programFilters }))

    this.router
      .navigate([], {
        relativeTo: this.activatedRoute,
        queryParams: programFilters,
      })
      .then()
  }

  resetFilters() {
    Object.keys(this.appliedFilters).forEach(key => {
      this.appliedFilters[key] = null
    })

    this.store.dispatch(ProgramsActions.getAllPrograms({ filters: {} }))

    this.router
      .navigate([], {
        relativeTo: this.activatedRoute,
        queryParams: {},
      })
      .then()
  }

  ngOnDestroy() {
    this.urlParamsSubscription.unsubscribe()
    this.programsSubscription.unsubscribe()
  }
}
