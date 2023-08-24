import { Injectable } from '@angular/core'
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router'
import { Observable } from 'rxjs'
import { AuthService } from '@app/modules/auth'
import { map } from 'rxjs/operators'

@Injectable()
export class PaidAccountGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot,
  ): Observable<boolean | UrlTree> | Promise<boolean> | boolean | UrlTree {
    return this.authService.getUserByToken().pipe(map(user => (user?.isPaid ? true : this.router.parseUrl('/upgrade'))))
  }
}
