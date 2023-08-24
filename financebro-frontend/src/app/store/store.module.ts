import { CommonModule } from '@angular/common'
import { NgModule } from '@angular/core'
import { EffectsModule } from '@ngrx/effects'
import { StoreModule } from '@ngrx/store'
import { StoreDevtoolsModule } from '@ngrx/store-devtools'
import { environment } from '@environments/environment'
import { appReducer } from '@store/app.reducer'
import { ProgramsEffects } from '@pages/programs/store/programs.effects'
import { RouterStateModule } from '@store/router/routerstate.module'

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterStateModule,
    StoreModule.forRoot(appReducer),
    EffectsModule.forRoot([ProgramsEffects]),
    !environment.production ? StoreDevtoolsModule.instrument() : [],
  ],
})
export class RootStoreModule {}
