import { NgModule } from '@angular/core'
import { CommonModule } from '@angular/common'
import { RouterModule } from '@angular/router'
import { PricingComponent } from './pricing.component'
import { ModalsModule, WidgetsModule } from '@app/_metronic/partials'
import { InlineSVGModule } from 'ng-inline-svg-2'

@NgModule({
  declarations: [PricingComponent],
  imports: [
    CommonModule,
    RouterModule.forChild([
      {
        path: '',
        component: PricingComponent,
      },
    ]),
    WidgetsModule,
    ModalsModule,
    InlineSVGModule,
  ],
})
export class PricingModule {}
