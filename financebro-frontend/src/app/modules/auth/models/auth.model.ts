export class AuthModel {
  authToken: string

  setAuth(resp: LoginResponseModel) {
    this.authToken = resp.key
  }
}

export class LoginResponseModel {
  key: string
}
