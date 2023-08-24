import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core'
import { Subscription } from 'rxjs'
import { Store } from '@ngrx/store'
import { MatTableDataSource } from '@angular/material/table'
import { MatDialog } from '@angular/material/dialog'
import { animate, state, style, transition, trigger } from '@angular/animations'
import * as fromApp from '@store/app.reducer'
import { programsFeatureKey } from './store/programs.reducer'
import { Program } from '@models/program'
import { FiltersDropdownDialogComponent } from '@pages/programs/filters-dropdown/filters-dropdown.component'
import { ActivatedRoute, Params } from '@angular/router'
import { ProgramsActions } from '@pages/programs/store/programs.actions'
import { MatSnackBar } from '@angular/material/snack-bar'
import { MatSort } from '@angular/material/sort'
import { CommonService } from '@shared/services/common.service'
import { AuthService } from '@app/modules/auth'

@Component({
  selector: 'app-programs',
  templateUrl: './programs.component.html',
  styleUrls: ['./programs.component.scss'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({ height: '0px', minHeight: '0' })),
      state('expanded', style({ height: '*' })),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
})
export class ProgramsComponent implements OnInit, OnDestroy {
  @ViewChild('filtersDropdownMenuButton') filtersDropdownMenuButton: ElementRef
  @ViewChild(MatSort) sort: MatSort

  programsSubscription: Subscription
  urlParamsSubscription: Subscription
  programFilters: Params = {}
  isLoading = true
  loading = true
  programsDataSource = new MatTableDataSource()
  totalRows: number
  displayedColumns = ['company', 'title', 'deadline', 'city', 'country', 'expand', 'actions']
  expandedElement: Program | null

  constructor(
    private readonly store: Store<fromApp.AppState>,
    public readonly authService: AuthService,
    public dialog: MatDialog,
    private activatedRoute: ActivatedRoute,
    private _snackBar: MatSnackBar,
    public commonService: CommonService,
  ) {}

  ngOnInit() {
    this.store.dispatch(ProgramsActions.getAllAvailableFilters())
    this.setupUrlParamsSubscription()
    this.setupProgramsSubscription()
    this.load()
  }

  setupUrlParamsSubscription() {
    this.urlParamsSubscription = this.activatedRoute.queryParams.subscribe(params => {
      this.loading = true
      this.programFilters = { ...params }
    })
  }

  load() {
    this.store.dispatch(ProgramsActions.getAllPrograms({ filters: this.programFilters }))
  }

  private setupProgramsSubscription() {
    this.programsSubscription = this.store.select(programsFeatureKey).subscribe(({ programs, total, isLoading }) => {
      this.isLoading = false
      if (this.authService.currentUserValue?.isPaid) {
        this.programsDataSource.data = programs
      } else {
        const extraPrograms = programs.slice(0, 5)
        this.programsDataSource.data = [...programs, ...extraPrograms]
      }
      this.programsDataSource.sortingDataAccessor = (item: any, property: string) => {
        switch (property) {
          case 'deadline':
            return new Date(item.deadline).getTime()
          default:
            return item[property]
        }
      }
      this.programsDataSource.sort = this.sort
      this.totalRows = total
    })
  }

  stopLoading() {
    if (this.totalRows !== -1) {
      this.loading = false
    }
  }

  applySearchFilter(event: KeyboardEvent) {
    const filterValue = (event.target as HTMLInputElement).value
    this.programsDataSource.filter = filterValue.trim().toLowerCase()
  }

  addProgramToFavorites(programId: number) {
    this.store.dispatch(ProgramsActions.addProgramToFavorites({ programId }))
    this._snackBar.open('Program added to favorites')
  }

  removeProgramFromFavorites(programId: number) {
    this.store.dispatch(ProgramsActions.removeProgramFromFavorites({ programId }))
    this._snackBar.open('Program removed from favorites')
  }

  openFiltersDropdownDialog() {
    this.dialog.open(FiltersDropdownDialogComponent, {
      restoreFocus: false,
      data: { positionRelativeToElement: this.filtersDropdownMenuButton },
    })
  }

  ngOnDestroy() {
    this.programsSubscription.unsubscribe()
    this.urlParamsSubscription.unsubscribe()
  }
}
