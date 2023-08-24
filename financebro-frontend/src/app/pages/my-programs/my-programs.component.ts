import { Component, OnInit, ViewChild } from '@angular/core'
import { Router } from '@angular/router'
import { ApiService } from '@shared/services/api.service'
import { finalize } from 'rxjs/operators'
import { MatTableDataSource } from '@angular/material/table'
import { UserProgram } from '@models/program'
import { MatSnackBar } from '@angular/material/snack-bar'
import { MatSort } from '@angular/material/sort'
import { CommonService } from '@shared/services/common.service'

@Component({
  selector: 'app-my-programs',
  templateUrl: './my-programs.component.html',
  styleUrls: ['./my-programs.component.scss'],
})
export class MyProgramsComponent implements OnInit {
  @ViewChild(MatSort) sort: MatSort

  loading = true
  programs: Array<UserProgram> = []
  programsDataSource = new MatTableDataSource()
  columnsToDisplay = [
    'company',
    'title',
    'deadline',
    'is_application_open',
    'city',
    'country',
    'current_stage',
    'actions',
  ]

  constructor(
    private router: Router,
    private readonly apiService: ApiService,
    private _snackBar: MatSnackBar,
    public commonService: CommonService,
  ) {}

  async ngOnInit() {
    this.apiService
      .getUserPrograms()
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(({ programs }) => {
        this.programs = programs
        this.programsDataSource.data = this.programs
        this.programsDataSource.sortingDataAccessor = (item: any, property: string) => {
          switch (property) {
            case 'deadline':
              return new Date(item.program.deadline).getTime()
            default:
              return item.program[property]
          }
        }
        this.programsDataSource.sort = this.sort
      })
  }

  removeProgram(id: number) {
    if (!this.programs.find((program: UserProgram) => program.program.id === id)) {
      return
    }

    this.programs = this.programs.filter((program: UserProgram) => program.program.id !== id)
    this.programsDataSource.data = this.programs

    this.apiService.toggleProgramFavorite({ program_id: id, set_favorite: false }).subscribe()
    this._snackBar.open('Program has been removed')
  }
}
