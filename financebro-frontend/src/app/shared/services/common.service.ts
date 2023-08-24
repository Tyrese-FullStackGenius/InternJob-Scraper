import { Injectable } from '@angular/core'

@Injectable({
  providedIn: 'root',
})
export class CommonService {
  getCompanyImagePath(companyName: string): string {
    return `/assets/media/banks/${companyName.toLowerCase().replace(/ /g, '_')}.svg`
  }

  getCountryFlagPath(code: string): string {
    return `/assets/media/flags-svg/${code}.svg`
  }
}
