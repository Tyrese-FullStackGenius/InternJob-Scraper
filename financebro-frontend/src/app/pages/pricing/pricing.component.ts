import { Component } from '@angular/core'
import { ApiService } from '@shared/services/api.service'
import { environment } from '@environments/environment'
import { finalize } from 'rxjs/operators'
import { Product, ProductKeys } from '@shared/interfaces'

@Component({
  selector: 'app-pricing',
  templateUrl: './pricing.component.html',
  styleUrls: ['./pricing.component.scss'],
})
export class PricingComponent {
  readonly products = environment.products
  loading = false

  constructor(private readonly apiService: ApiService) {}

  upgrade(productKey: ProductKeys) {
    this.loading = true
    const product: Product | undefined = this.products.get(productKey)
    if (product) {
      this.apiService
        .upgradeAccount(product.id)
        .pipe(finalize(() => (this.loading = false)))
        .subscribe(async response => {
          window.location.href = response.redirect_url
        })
    }
  }
}
