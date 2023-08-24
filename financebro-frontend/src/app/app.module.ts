import { NgModule, APP_INITIALIZER } from '@angular/core'
import { BrowserModule } from '@angular/platform-browser'
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http'
import { ClipboardModule } from 'ngx-clipboard'
import { TranslateModule } from '@ngx-translate/core'
import { InlineSVGModule } from 'ng-inline-svg-2'
import { NgbModule } from '@ng-bootstrap/ng-bootstrap'
import { AppRoutingModule } from './app-routing.module'
import { AppComponent } from './app.component'
import { AuthService } from '@app/modules/auth'
import { ApiInterceptor } from '@shared/services/api.interceptor'
import { environment } from '@environments/environment'
import { ProgramsComponent } from '@pages/programs/programs.component'
import { FiltersDropdownDialogComponent } from '@pages/programs/filters-dropdown/filters-dropdown.component'
import { StoreRouterConnectingModule } from '@ngrx/router-store'
import { StoreDevtoolsModule } from '@ngrx/store-devtools'
import { RootStoreModule } from '@store/store.module'
import { AngularMaterialModule } from 'app/angular-material.module'
import { FormsModule, ReactiveFormsModule } from '@angular/forms'
import { MyProgramsComponent } from '@pages/my-programs/my-programs.component'
import { MyPreferencesComponent } from '@pages/my-preferences/my-preferences.component'
import { EmailPreferencesComponent } from '@pages/email-preferences/email-preferences.component'
import { ProgramDetailsComponent } from '@pages/program-details/program-details.component'
import { SubmittedDialogComponent } from '@pages/program-details/dialogs/submitted.dialog'
import { OnlineTestDialogComponent } from '@pages/program-details/dialogs/online-test.dialog'
import { PreRecordedVideoInterviewDialogComponent } from '@pages/program-details/dialogs/pre-recorded-video-interview.dialog'
import { PersonalInterviewDialogComponent } from '@pages/program-details/dialogs/personal-interview.dialog'
import { CloseDialogComponent } from '@pages/program-details/dialogs/close.dialog'
import { MatTooltipModule } from '@angular/material/tooltip'
import { MatSortModule } from '@angular/material/sort'
import { MAT_SNACK_BAR_DEFAULT_OPTIONS } from '@angular/material/snack-bar'
import { ContentReduceViewComponent } from '@shared/components/content-reduce-view/content-reduce-view.component'
import { PluckPipe } from '@shared/pipes/pluck.pipe'
import { PaymentSuccessComponent } from '@pages/payment-success/payment-success.component'
import { SharedModule } from '@shared/shared/shared.module'
import { UpgradeComponent } from '@pages/upgrade/upgrade.component'

function appInitializer(authService: AuthService) {
  return () => {
    return new Promise(resolve => {
      //@ts-ignore
      authService.getUserByToken().subscribe().add(resolve)
    })
  }
}

@NgModule({
  declarations: [
    ContentReduceViewComponent,
    AppComponent,
    ProgramsComponent,
    PaymentSuccessComponent,
    ProgramDetailsComponent,
    MyProgramsComponent,
    MyPreferencesComponent,
    EmailPreferencesComponent,
    FiltersDropdownDialogComponent,
    CloseDialogComponent,
    OnlineTestDialogComponent,
    PersonalInterviewDialogComponent,
    PreRecordedVideoInterviewDialogComponent,
    SubmittedDialogComponent,
    UpgradeComponent,
    PluckPipe,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule,
    TranslateModule.forRoot(),
    HttpClientModule,
    ClipboardModule,
    AngularMaterialModule,
    RootStoreModule,
    AppRoutingModule,
    InlineSVGModule.forRoot(),
    NgbModule,
    StoreRouterConnectingModule.forRoot(),
    StoreDevtoolsModule.instrument({ maxAge: 25, logOnly: environment.production }),
    MatTooltipModule,
    MatSortModule,
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: appInitializer,
      multi: true,
      deps: [AuthService],
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ApiInterceptor,
      multi: true,
      // deps: [AuthService],
    },
    { provide: MAT_SNACK_BAR_DEFAULT_OPTIONS, useValue: { duration: 2500 } },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
