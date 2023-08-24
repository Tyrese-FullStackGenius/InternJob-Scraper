import { Injectable, OnDestroy } from '@angular/core'
import { BehaviorSubject, Observable, of, Subscription } from 'rxjs'
import { catchError, finalize, map, switchMap } from 'rxjs/operators'
import { UserModel } from '@app/modules/auth'
import { AuthModel, LoginResponseModel } from '../models/auth.model'
import { AuthHTTPService } from './auth-http'
import { Router } from '@angular/router'
import { AuthStorageService } from '@app/modules/auth/services/auth.storage.service'

export type UserType = UserModel | undefined

@Injectable({
  providedIn: 'root',
})
export class AuthService implements OnDestroy {
  private unsubscribe: Subscription[] = []

  currentUser$: Observable<UserType>
  isLoading$: Observable<boolean>
  currentUserSubject: BehaviorSubject<UserType>
  isLoadingSubject: BehaviorSubject<boolean>

  get currentUserValue(): UserType {
    return this.currentUserSubject.value
  }

  set currentUserValue(user: UserType) {
    this.currentUserSubject.next(user)
  }

  constructor(
    private authHttpService: AuthHTTPService,
    private router: Router,
    private authStorageService: AuthStorageService,
  ) {
    this.isLoadingSubject = new BehaviorSubject<boolean>(false)
    this.currentUserSubject = new BehaviorSubject<UserType>(undefined)
    this.currentUser$ = this.currentUserSubject.asObservable()
    this.isLoading$ = this.isLoadingSubject.asObservable()
    /*const subscr = this.getUserByToken().subscribe()
    this.unsubscribe.push(subscr)*/
  }

  login(username: string, password: string): Observable<UserType> {
    this.isLoadingSubject.next(true)
    return this.authHttpService.login(username, password).pipe(
      map((resp: LoginResponseModel) => {
        let auth: AuthModel = new AuthModel()
        auth.setAuth(resp)
        return this.setAuthFromLocalStorage(auth)
      }),
      switchMap(() => this.getUserByToken()),
      catchError(err => {
        console.error('err', err)
        return of(undefined)
      }),
      finalize(() => this.isLoadingSubject.next(false)),
    )
  }

  logout() {
    this.authStorageService.removeAuthData()
    if (this.currentUserValue) {
      this.isLoadingSubject.next(true)
      this.authHttpService.logout().subscribe()
      this.isLoadingSubject.next(false)
    }
    this.router
      .navigate(['/auth/login'], {
        queryParams: {},
      })
      .then()
  }

  getUserByToken(): Observable<UserType> {
    const auth = this.authStorageService.getAuthFromLocalStorage()
    if (!auth || !auth.authToken) {
      return of(undefined)
    }

    this.isLoadingSubject.next(true)
    return this.authHttpService.getUserByToken(auth.authToken).pipe(
      map((user: UserType) => {
        const userObj = new UserModel()
        userObj.setUser(user)
        if (user) {
          this.currentUserSubject.next(userObj)
        } else {
          this.logout()
        }
        return userObj
      }),
      finalize(() => this.isLoadingSubject.next(false)),
    )
  }

  // need create new user then login
  registration(user: UserModel): Observable<any> {
    this.isLoadingSubject.next(true)
    return this.authHttpService.createUser(user).pipe(
      map((resp: LoginResponseModel) => {
        let auth: AuthModel = new AuthModel()
        auth.setAuth(resp)
        return this.setAuthFromLocalStorage(auth)
      }),
      switchMap(() => this.getUserByToken()),
      catchError(err => {
        return of({ error: err.error })
      }),
      finalize(() => this.isLoadingSubject.next(false)),
    )
  }

  forgotPassword(email: string): Observable<boolean> {
    this.isLoadingSubject.next(true)
    return this.authHttpService.forgotPassword(email).pipe(finalize(() => this.isLoadingSubject.next(false)))
  }

  // private methods
  private setAuthFromLocalStorage(auth: AuthModel): boolean {
    if (auth && auth.authToken) {
      this.authStorageService.setAuthData(auth)
      return true
    }
    return false
  }

  ngOnDestroy() {
    this.unsubscribe.forEach(sb => sb.unsubscribe())
  }
}
