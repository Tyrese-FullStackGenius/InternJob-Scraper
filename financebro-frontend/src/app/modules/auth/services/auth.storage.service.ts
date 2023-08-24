import { Injectable } from '@angular/core'
import { AuthModel } from '@app/modules/auth/models/auth.model'
import { environment } from '@environments/environment'

@Injectable({
  providedIn: 'root',
})
export class AuthStorageService {
  private readonly authLocalStorageToken = `${environment.appVersion}-${environment.USERDATA_KEY}`

  constructor() {}

  getAuthData(): string | null {
    return localStorage.getItem(this.authLocalStorageToken)
  }

  setAuthData(auth: AuthModel) {
    localStorage.setItem(this.authLocalStorageToken, JSON.stringify(auth))
  }

  removeAuthData() {
    localStorage.removeItem(this.authLocalStorageToken)
  }

  getAuthFromLocalStorage(): AuthModel | undefined {
    try {
      const lsValue = this.getAuthData()
      if (!lsValue) {
        return undefined
      }
      return JSON.parse(lsValue)
    } catch (error) {
      console.error(error)
      return undefined
    }
  }
}
