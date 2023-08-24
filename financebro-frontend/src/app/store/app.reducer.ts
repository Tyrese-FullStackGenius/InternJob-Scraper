import { ActionReducerMap } from '@ngrx/store'
import * as fromPrograms from '@pages/programs/store/programs.reducer'

export interface AppState {
  programs: fromPrograms.State
}

export const appReducer: ActionReducerMap<AppState> = {
  programs: fromPrograms.programsReducer,
}
