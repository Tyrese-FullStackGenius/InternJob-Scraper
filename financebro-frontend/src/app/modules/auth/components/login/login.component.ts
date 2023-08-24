import { Component, OnInit, OnDestroy } from '@angular/core'
import { FormBuilder, FormGroup, Validators } from '@angular/forms'
import { Subscription, Observable } from 'rxjs'
import { first } from 'rxjs/operators'
import { UserModel } from '@app/modules/auth'
import { AuthService } from '@app/modules/auth'
import { ActivatedRoute, Router } from '@angular/router'

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit, OnDestroy {
  // KeenThemes mock, change it to:
  loginForm: FormGroup
  hasError: boolean
  returnUrl: string
  isLoading$: Observable<boolean>
  signup: boolean

  // private fields
  private unsubscribe: Subscription[] = [] // Read more: => https://brianflove.com/2016/12/11/anguar-2-unsubscribe-observables/

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router,
  ) {
    this.signup = Boolean(route.snapshot.queryParams.signup)
    this.isLoading$ = this.authService.isLoading$
    // redirect to home if already logged in
    if (this.authService.currentUserValue) {
      this.router.navigate(['/']).then()
    }
  }

  ngOnInit(): void {
    this.initForm()
    // get return url from route parameters or default to '/'
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'.toString()] || '/'
  }

  // convenience getter for easy access to form fields
  get f() {
    return this.loginForm.controls
  }

  initForm() {
    this.loginForm = this.fb.group({
      email: [
        '',
        Validators.compose([
          Validators.required,
          Validators.email,
          Validators.minLength(3),
          Validators.maxLength(320), // https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
        ]),
      ],
      password: ['', Validators.compose([Validators.required, Validators.minLength(3), Validators.maxLength(100)])],
    })
  }

  submit() {
    this.hasError = false
    const loginSubscr = this.authService
      .login(this.f.email.value, this.f.password.value)
      .pipe(first())
      .subscribe((user: UserModel | undefined) => {
        if (user) {
          this.router.navigate([this.returnUrl]).then()
        } else {
          this.hasError = true
        }
      })
    this.unsubscribe.push(loginSubscr)
  }

  ngOnDestroy() {
    this.unsubscribe.forEach(sb => sb.unsubscribe())
  }
}
