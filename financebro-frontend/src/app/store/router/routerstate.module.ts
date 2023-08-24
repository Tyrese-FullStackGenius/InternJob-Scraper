import { NgModule } from '@angular/core'
import { CommonModule } from '@angular/common'
import { StoreModule } from '@ngrx/store'

import { StoreRouterConnectingModule, RouterState, routerReducer } from '@ngrx/router-store'

export const routerStateConfig = {
  stateKey: 'router',
}

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    StoreModule.forFeature(routerStateConfig.stateKey, routerReducer),
    StoreRouterConnectingModule.forRoot({
      routerState: RouterState.Minimal,
    }),
  ],
})
export class RouterStateModule {}
