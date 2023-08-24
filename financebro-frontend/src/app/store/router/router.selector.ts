import * as fromRouter from '@ngrx/router-store'
import { createFeatureSelector } from '@ngrx/store'

export interface State {
  router: fromRouter.RouterReducerState
}

export const selectRouter = createFeatureSelector<fromRouter.RouterReducerState>('router')

export const { selectQueryParams } = fromRouter.getSelectors(selectRouter)
