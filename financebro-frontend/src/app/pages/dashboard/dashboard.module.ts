import { NgModule } from '@angular/core'
import { CommonModule } from '@angular/common'
import { RouterModule } from '@angular/router'
import { DashboardComponent } from './dashboard.component'
import { ModalsModule, WidgetsModule } from '@app/_metronic/partials'
import { InlineSVGModule } from 'ng-inline-svg-2'
import { MatProgressBarModule } from '@angular/material/progress-bar'

@NgModule({
  declarations: [DashboardComponent],
  imports: [
    CommonModule,
    RouterModule.forChild([
      {
        path: '',
        component: DashboardComponent,
      },
    ]),
    WidgetsModule,
    InlineSVGModule,
    ModalsModule,
    MatProgressBarModule,
  ],
})
export class DashboardModule {}
