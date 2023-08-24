import { createAction, props } from '@ngrx/store'
import { Program, AvailableFilters } from '@models/program'
import { Params } from '@angular/router'

export namespace ProgramsActions {
  export const getAllPrograms = createAction(
    '[Programs] Search Programs',
    props<{
      filters: Params
    }>(),
  )

  export const getAllProgramsSuccess = createAction(
    '[Programs] Get programs success',
    props<{
      favorite_programs: number[]
      programs: Program[]
      total: number
    }>(),
  )

  export const getAllProgramsFailure = createAction(
    '[Programs] Get programs failure',
    props<{
      error: Error
    }>(),
  )

  export const addProgramToFavorites = createAction(
    '[Programs] Add program to favorites',
    props<{ programId: number }>(),
  )

  export const removeProgramFromFavorites = createAction(
    '[Programs] Remove program from favorites',
    props<{ programId: number }>(),
  )

  export const updateFavoriteProgramsList = createAction('[Programs] Update favorite programs list')

  export const resetState = createAction('[Programs] Reset State')

  export const getAllAvailableFilters = createAction('[Programs] Get All Available Filters')

  export const getAllAvailableFiltersSuccess = createAction(
    '[Programs] Get All Available Filters Success',
    props<{
      filters: AvailableFilters
    }>(),
  )

  export const getAllAvailableFiltersFailure = createAction(
    '[Programs] Get All Available Filters Failure',
    props<{
      error: Error
    }>(),
  )
}
