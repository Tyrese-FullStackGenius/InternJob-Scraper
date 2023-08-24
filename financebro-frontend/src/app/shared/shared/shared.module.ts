import { NgModule } from '@angular/core'
import { CommonModule } from '@angular/common'
import { UpgradeAccountComponent } from '@shared/components/upgrade-account/upgrade-account.component'

@NgModule({
  declarations: [UpgradeAccountComponent],
  imports: [CommonModule],
  exports: [UpgradeAccountComponent],
})
export class SharedModule {}
