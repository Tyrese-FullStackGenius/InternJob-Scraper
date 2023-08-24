import { Routes } from '@angular/router'
import { ProgramsComponent } from './programs/programs.component'
import { MyProgramsComponent } from '@pages/my-programs/my-programs.component'
import { ProgramDetailsComponent } from '@pages/program-details/program-details.component'
import { MyPreferencesComponent } from '@pages/my-preferences/my-preferences.component'
import { EmailPreferencesComponent } from '@pages/email-preferences/email-preferences.component'
import { PaymentSuccessComponent } from '@pages/payment-success/payment-success.component'
import { PaidAccountGuard } from '@shared/guards/paid-account.guard'
import { UpgradeComponent } from '@pages/upgrade/upgrade.component'

const Routing: Routes = [
  {
    path: 'upgrade',
    component: UpgradeComponent,
  },
  {
    path: 'programs',
    component: ProgramsComponent,
  },
  {
    path: 'my-programs',
    component: MyProgramsComponent,
    canActivate: [PaidAccountGuard],
  },
  {
    path: 'program/:id',
    component: ProgramDetailsComponent,
  },
  {
    path: 'my-preferences',
    component: MyPreferencesComponent,
    canActivate: [PaidAccountGuard],
  },
  {
    path: 'email-preferences',
    component: EmailPreferencesComponent,
    canActivate: [PaidAccountGuard],
  },
  {
    path: 'customer-info',
    loadChildren: () => import('./customer-info/customer-info.module').then(m => m.CustomerInfoModule),
  },
  {
    path: 'dashboard',
    loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule),
  },
  {
    path: 'pricing',
    loadChildren: () => import('./pricing/pricing.module').then(m => m.PricingModule),
  },
  {
    path: 'payment/success',
    component: PaymentSuccessComponent,
  },
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: 'error/404',
  },
]

export { Routing }
