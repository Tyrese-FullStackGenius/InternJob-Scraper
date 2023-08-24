import { Injectable } from '@angular/core'
import { Actions, createEffect, ofType } from '@ngrx/effects'
import { of } from 'rxjs'
import { catchError, switchMap } from 'rxjs/operators'
import { ProgramsResource, AvailableFiltersResource } from '@models/program'
import { ApiService } from '@shared/services/api.service'
import { ProgramsActions } from './programs.actions'

@Injectable()
export class ProgramsEffects {
  getAllPrograms = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProgramsActions.getAllPrograms),
      switchMap(action => {
        return this.apiService.getAllPrograms(action.filters).pipe(
          switchMap((resp: ProgramsResource) => [
            ProgramsActions.getAllProgramsSuccess(resp),
            ProgramsActions.updateFavoriteProgramsList(),
          ]),
          catchError(error => {
            return of(ProgramsActions.getAllProgramsFailure({ error }))
          }),
        )
      }),
    )
  })

  getAllAvailableFilters = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProgramsActions.getAllAvailableFilters),
      switchMap(() => {
        return this.apiService.getAllAvailableFilters().pipe(
          switchMap((resp: AvailableFiltersResource) => [ProgramsActions.getAllAvailableFiltersSuccess(resp)]),
          catchError(error => {
            return of(ProgramsActions.getAllAvailableFiltersFailure({ error }))
          }),
        )
      }),
    )
  })

  addProgramToFavorites = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProgramsActions.addProgramToFavorites),
      switchMap(action => {
        return this.apiService
          .toggleProgramFavorite({ program_id: action.programId, set_favorite: true })
          .pipe(switchMap(() => [ProgramsActions.updateFavoriteProgramsList()]))
      }),
    )
  })

  removeProgramToFavorites = createEffect(() => {
    return this.actions$.pipe(
      ofType(ProgramsActions.removeProgramFromFavorites),
      switchMap(action => {
        return this.apiService
          .toggleProgramFavorite({ program_id: action.programId, set_favorite: false })
          .pipe(switchMap(() => [ProgramsActions.updateFavoriteProgramsList()]))
      }),
    )
  })

  constructor(private readonly actions$: Actions, private apiService: ApiService) {}
}
