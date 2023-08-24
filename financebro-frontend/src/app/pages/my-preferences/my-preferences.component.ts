import { Component, OnDestroy, OnInit } from '@angular/core'
import { FormGroup, NonNullableFormBuilder } from '@angular/forms'
import { finalize, switchMap } from 'rxjs/operators'
import { ApiService } from '@shared/services/api.service'
import { forkJoin, Subscription } from 'rxjs'
import { UserProgramPreferences } from '@pages/my-preferences/dto/user-program-preferences.dto'
import { AllPreferences } from '@models/generic'

@Component({
  selector: 'app-my-preferences',
  templateUrl: './my-preferences.component.html',
  styleUrls: ['./my-preferences.component.scss'],
})
export class MyPreferencesComponent implements OnInit, OnDestroy {
  form: FormGroup
  form$: Subscription
  loading = true
  preferences: UserProgramPreferences
  allPreferences: AllPreferences

  constructor(private fb: NonNullableFormBuilder, public readonly apiService: ApiService) {}

  ngOnInit() {
    this.form = this.fb.group({
      company_categories: [[]],
      program_categories: [[]],
      regions: [[]],
    })

    this.form$ = this.form.valueChanges
      .pipe(switchMap(formValue => this.apiService.saveUserProgramPreferences(formValue)))
      .subscribe()

    const filters$ = this.apiService.getAllAvailableFilters()
    const userPreferences$ = this.apiService.getUserProgramPreferences()

    forkJoin({ filters: filters$, userPreferences: userPreferences$ })
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(({ filters, userPreferences }) => {
        this.preferences = userPreferences
        this.allPreferences = filters.filters
        this.form.setValue(this.preferences)
      })
  }

  ngOnDestroy() {
    this.form$.unsubscribe()
  }
}
