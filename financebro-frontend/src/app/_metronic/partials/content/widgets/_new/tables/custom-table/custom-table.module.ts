import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';
import { CustomTableComponent } from './custom-table.component';
import { ModalsModule, WidgetsModule } from '../../../../../../partials';
import { Routing } from '../../../../../../../pages/routing';
const routes: Routes = [
  {
    path: '',
    component: CustomTableComponent,
    children: Routing,
  },
];
@NgModule({
  declarations: [CustomTableComponent],
  imports: [
    CommonModule,
    RouterModule.forRoot(routes),
    WidgetsModule,
    ModalsModule,
  ],
  exports: [RouterModule]
})
export class CustomTableModule {}
