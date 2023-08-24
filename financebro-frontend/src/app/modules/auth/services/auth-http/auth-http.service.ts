import { Injectable } from '@angular/core'
import { Observable } from 'rxjs'
import { HttpClient, HttpHeaders } from '@angular/common/http'
import { UserModel } from '@app/modules/auth'
import { environment } from '@environments/environment'
import { LoginResponseModel } from '../../models/auth.model'

@Injectable({
  providedIn: 'root',
})
export class AuthHTTPService {
  constructor(private http: HttpClient) {}

  // public methods
  login(username: string, password: string): Observable<any> {
    return this.http.post<LoginResponseModel>(`${environment.apiUrl}/auth/login/`, {
      username,
      password,
    })
  }

  logout(): Observable<any> {
    return this.http.post(`${environment.apiUrl}/auth/logout/`, {})
  }

  createUser(user: UserModel): Observable<any> {
    return this.http.post<LoginResponseModel>(`${environment.apiUrl}/auth/register/`, {
      email: user.email,
      password1: user.password,
      password2: user.password,
    })
  }

  // Your server should check email => If email exists send link to the user and return true | If email doesn't exist return false
  forgotPassword(email: string): Observable<boolean> {
    return this.http.post<boolean>(`${environment.apiUrl}/auth/forgot-password`, {
      email,
    })
  }

  getUserByToken(token: string): Observable<UserModel> {
    /*const httpHeaders = new HttpHeaders({
      Authorization: `Bearer ${token}`,
    })*/
    return this.http.get<UserModel>(`${environment.apiUrl}/api/me`)
  }
}
