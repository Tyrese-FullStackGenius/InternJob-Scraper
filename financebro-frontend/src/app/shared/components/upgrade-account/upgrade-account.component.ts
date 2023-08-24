import { Component, Input } from '@angular/core'
import { Router } from '@angular/router'

@Component({
  selector: 'app-upgrade-account',
  templateUrl: './upgrade-account.component.html',
  styleUrls: ['./upgrade-account.component.scss'],
})
export class UpgradeAccountComponent {
  @Input() text: string = 'Upgrade'
  @Input() scaled = false
  @Input() shadowed = false

  constructor(private readonly router: Router) {}

  async upgrade() {
    await this.router.navigateByUrl('/pricing')
  }
}
