import { Component, OnInit } from '@angular/core'
import { MatSnackBar } from '@angular/material/snack-bar'
import { Router } from '@angular/router'
import { ApiService } from '@shared/services/api.service'
import { finalize } from 'rxjs/operators'
import { DashboardDataDto } from '@pages/dashboard/dto/dashboard-data.dto'

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  data: DashboardDataDto
  loading = true

  constructor(private _snackBar: MatSnackBar, private router: Router, private readonly apiService: ApiService) {}

  ngOnInit() {
    this.apiService
      .getDashboardData()
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(response => {
        this.data = response
      })
  }
}
