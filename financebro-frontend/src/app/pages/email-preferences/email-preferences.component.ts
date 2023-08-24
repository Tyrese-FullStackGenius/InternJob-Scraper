import { Component, OnDestroy, OnInit } from '@angular/core'
import { FormControl, FormGroup, NonNullableFormBuilder } from '@angular/forms'
import { ApiService } from '@shared/services/api.service'
import { finalize, switchMap } from 'rxjs/operators'
import { forkJoin, Subscription } from 'rxjs'
import { EmailPreferences } from '@pages/email-preferences/dto/email-preferences.dto'
import { AllPreferences } from '@models/generic'

@Component({
  selector: 'app-email-preferences',
  templateUrl: './email-preferences.component.html',
  styleUrls: ['./email-preferences.component.scss'],
})
export class EmailPreferencesComponent implements OnInit, OnDestroy {
  readonly emailPerDayRange = [...Array(10).keys()]
  form: FormGroup
  form$: Subscription
  loading = true
  preferences: EmailPreferences
  allPreferences: AllPreferences

  constructor(private fb: NonNullableFormBuilder, public readonly apiService: ApiService) {}

  ngOnInit() {
    this.form = this.fb.group({
      company_categories: [[]],
      email_notifications_enabled: [false],
      emails_per_day_count: new FormControl<number | null>(null),
      near_deadline_notifications_enabled: [false],
      program_categories: [[]],
      regions: [[]],
    })

    this.form$ = this.form.valueChanges
      .pipe(switchMap(formValue => this.apiService.saveEmailProgramPreferences(formValue)))
      .subscribe()

    const filters$ = this.apiService.getAllAvailableFilters()
    const emailPreferences$ = this.apiService.getUserEmailPreferences()

    forkJoin({ filters: filters$, emailPreferences: emailPreferences$ })
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(({ filters, emailPreferences }) => {
        this.preferences = emailPreferences
        this.allPreferences = filters.filters
        this.form.setValue(this.preferences)
      })
  }

  ngOnDestroy() {
    this.form$.unsubscribe()
  }
}
