import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpStatusCode,
} from '@angular/common/http'
import { Observable, throwError } from 'rxjs'
import { catchError, map } from 'rxjs/operators'
import { Injectable } from '@angular/core'
import { environment } from '@environments/environment'
import { AuthModel } from '@app/modules/auth/models/auth.model'
import { Router } from '@angular/router'
import { AuthStorageService } from '@app/modules/auth/services/auth.storage.service'
import { AuthService } from '@app/modules/auth'

@Injectable()
export class ApiInterceptor implements HttpInterceptor {
  constructor(
    private router: Router,
    private authStorageService: AuthStorageService,
    private authService: AuthService,
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (req.url.startsWith(environment.apiUrl)) {
      const authData: AuthModel | undefined = this.authStorageService.getAuthFromLocalStorage()
      if (authData?.authToken) {
        req = req.clone({
          headers: req.headers.set('Authorization', `Bearer ${authData?.authToken}`),
        })
      }
    }

    return next.handle(req).pipe(
      map((event: HttpEvent<any>) => {
        return event
      }),
      catchError((error: HttpErrorResponse) => {
        if ([HttpStatusCode.Unauthorized].includes(error.status)) {
          this.authService.logout()
          this.router.navigate(['/auth/login'])
        }
        return throwError(error)
      }),
    )
  }
}
