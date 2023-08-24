import { Component, OnInit } from '@angular/core'
import { FormBuilder, FormGroup } from '@angular/forms'
import { ApiService } from '@shared/services/api.service'
import { finalize } from 'rxjs/operators'
import { MatSnackBar } from '@angular/material/snack-bar'

@Component({
  selector: 'app-customer-info',
  templateUrl: './customer-info.component.html',
  styleUrls: ['./customer-info.component.scss'],
})
export class CustomerInfoComponent implements OnInit {
  form: FormGroup
  loading = true
  submitting = false

  constructor(
    private readonly fb: FormBuilder,
    public readonly apiService: ApiService,
    private _snackBar: MatSnackBar,
  ) {
    this.form = fb.group({
      first_name: [''],
      middle_name: [''],
      last_name: [''],
      email: [''],
      phone: [''],
      address1: [''],
      address2: [''],
      city: [''],
      country: [''],
      postal_code: [''],
      education1: [''],
      education2: [''],
      education3: [''],
      employment1: [''],
      employment2: [''],
      employment3: [''],
    })
  }

  ngOnInit() {
    this.apiService
      .getCustomerInfo()
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(response => {
        this.form.setValue(response)
      })
  }

  submit() {
    this.submitting = true
    this.apiService
      .saveCustomerInfo(this.form.value)
      .pipe(finalize(() => (this.submitting = false)))
      .subscribe(() => {
        this._snackBar.open('Chrome Extension Info updated!')
        window.postMessage({ type: 'appDataUpdated' }, '*')
      })
  }
}
