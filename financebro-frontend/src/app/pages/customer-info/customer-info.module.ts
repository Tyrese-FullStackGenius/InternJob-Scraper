import { NgModule } from '@angular/core'
import { CommonModule } from '@angular/common'
import { CustomerInfoComponent } from './customer-info.component'
import { RouterModule } from '@angular/router'
import { FormsModule, ReactiveFormsModule } from '@angular/forms'
import { MatCheckboxModule } from '@angular/material/checkbox'
import { MatFormFieldModule } from '@angular/material/form-field'
import { MatOptionModule } from '@angular/material/core'
import { MatProgressBarModule } from '@angular/material/progress-bar'
import { MatSelectModule } from '@angular/material/select'
import { AngularMaterialModule } from '@app/angular-material.module'

@NgModule({
  declarations: [CustomerInfoComponent],
  imports: [
    CommonModule,
    RouterModule.forChild([
      {
        path: '',
        component: CustomerInfoComponent,
      },
    ]),
    AngularMaterialModule,
    FormsModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatOptionModule,
    MatProgressBarModule,
    MatSelectModule,
    ReactiveFormsModule,
  ],
})
export class CustomerInfoModule {}
