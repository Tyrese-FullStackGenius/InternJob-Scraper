import { Component, OnInit, OnDestroy } from '@angular/core'
import { FormGroup, FormBuilder, Validators } from '@angular/forms'
import { Subscription, Observable } from 'rxjs'
import { Router } from '@angular/router'
import { AuthService } from '@app/modules/auth'
import { ConfirmPasswordValidator } from '@app/modules/auth'
import { UserModel } from '@app/modules/auth'

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.scss'],
})
export class RegistrationComponent implements OnInit, OnDestroy {
  registrationForm: FormGroup
  hasError = false
  errorMessage = ''
  isLoading$: Observable<boolean>

  private unsubscribe: Subscription[] = []

  constructor(private fb: FormBuilder, private authService: AuthService, private router: Router) {
    this.isLoading$ = this.authService.isLoading$
    if (this.authService.currentUserValue) {
      this.router.navigate(['/']).then()
    }
  }

  ngOnInit(): void {
    this.initForm()
  }

  // convenience getter for easy access to form fields
  get f() {
    return this.registrationForm.controls
  }

  initForm() {
    this.registrationForm = this.fb.group(
      {
        email: [
          '',
          Validators.compose([
            Validators.required,
            Validators.email,
            Validators.minLength(3),
            Validators.maxLength(320), // https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
          ]),
        ],
        password: ['', Validators.compose([Validators.required, Validators.minLength(8), Validators.maxLength(100)])],
        cPassword: ['', Validators.compose([Validators.required, Validators.minLength(8), Validators.maxLength(100)])],
        agree: [false, Validators.compose([Validators.requiredTrue])],
      },
      {
        validator: ConfirmPasswordValidator.MatchPassword,
      },
    )
  }

  submit() {
    this.errorMessage = ''
    this.hasError = false
    const result: {
      [key: string]: string
    } = {}
    Object.keys(this.f).forEach(key => {
      result[key] = this.f[key].value
    })
    const newUser = new UserModel()
    newUser.setUser(result)
    const registrationSubscription = this.authService.registration(newUser).subscribe(async response => {
      if (response.error) {
        this.hasError = true
        for (const [key, value] of Object.entries(response.error)) {
          this.errorMessage += (value as String[]).join('. ')
        }
      } else {
        await this.router.navigate(['/auth/login'], { queryParams: { signup: true } })
      }
    })
    this.unsubscribe.push(registrationSubscription)
  }

  ngOnDestroy() {
    this.unsubscribe.forEach(sb => sb.unsubscribe())
  }
}
