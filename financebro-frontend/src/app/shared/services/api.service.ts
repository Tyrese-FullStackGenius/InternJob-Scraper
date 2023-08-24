import { Injectable } from '@angular/core'
import { Observable, Subject, throwError } from 'rxjs'
import { HttpClient, HttpErrorResponse } from '@angular/common/http'
import { environment } from '@environments/environment'
import {
  ProgramsResource,
  UserProgram,
  UserProgramNoteDto,
  ToggleProgramFavoriteDto,
  UserProgramPipelineActionDto,
  UserProgramCommunityReportedData,
  UpgradeAccountDto,
  AvailableFiltersResource,
} from '@models/program'
import { Params } from '@angular/router'
import { catchError } from 'rxjs/operators'
import { UserProgramPreferences } from '@pages/my-preferences/dto/user-program-preferences.dto'
import { EmailPreferences } from '@pages/email-preferences/dto/email-preferences.dto'
import { DashboardDataDto } from '@pages/dashboard/dto/dashboard-data.dto'
import { CustomerInfoDto } from '@pages/customer-info/dto/customer-info.dto'

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  error$: Subject<string> = new Subject<string>()

  constructor(private http: HttpClient) {}

  fetchErrorFromResponse(errorResponse: HttpErrorResponse): string {
    return errorResponse.error.message ?? errorResponse.message
  }

  handleError(errorResponse: HttpErrorResponse) {
    const errorMessage = this.fetchErrorFromResponse(errorResponse)
    this.error$.next(errorMessage)
    return throwError(errorResponse)
  }

  getAllPrograms(filters: Params): Observable<any> {
    return this.http
      .get<ProgramsResource>(`${environment.apiUrl}/api/programs`, { params: filters })
      .pipe(catchError(err => this.handleError(err)))
  }

  getAllAvailableFilters(): Observable<any> {
    return this.http
      .get<AvailableFiltersResource>(`${environment.apiUrl}/api/available-filters`)
      .pipe(catchError(err => this.handleError(err)))
  }

  getUserPrograms(): Observable<any> {
    return this.http
      .get<ProgramsResource>(`${environment.apiUrl}/api/user-programs`)
      .pipe(catchError(err => this.handleError(err)))
  }

  getProgram(id: number): Observable<UserProgram> {
    return this.http
      .get<UserProgram>(`${environment.apiUrl}/api/user-program/${id}`)
      .pipe(catchError(err => this.handleError(err)))
  }

  getProgramCommunityReportedData(id: number): Observable<UserProgramCommunityReportedData> {
    return this.http
      .get<UserProgramCommunityReportedData>(`${environment.apiUrl}/api/program-community-reported-data/${id}`)
      .pipe(catchError(err => this.handleError(err)))
  }

  getDashboardData(): Observable<DashboardDataDto> {
    return this.http
      .get<DashboardDataDto>(`${environment.apiUrl}/api/dashboard-stats`)
      .pipe(catchError(err => this.handleError(err)))
  }

  getUserProgramPreferences(): Observable<UserProgramPreferences> {
    return this.http
      .get<UserProgramPreferences>(`${environment.apiUrl}/api/user-program-preferences`)
      .pipe(catchError(err => this.handleError(err)))
  }

  saveUserProgramPreferences(preferences: UserProgramPreferences): Observable<any> {
    return this.http
      .post<any>(`${environment.apiUrl}/api/user-program-preferences`, { ...preferences })
      .pipe(catchError(err => this.handleError(err)))
  }

  getUserEmailPreferences(): Observable<EmailPreferences> {
    return this.http
      .get<EmailPreferences>(`${environment.apiUrl}/api/user-email-preferences`)
      .pipe(catchError(err => this.handleError(err)))
  }

  saveEmailProgramPreferences(preferences: EmailPreferences): Observable<any> {
    return this.http
      .post<any>(`${environment.apiUrl}/api/user-email-preferences`, { ...preferences })
      .pipe(catchError(err => this.handleError(err)))
  }

  saveUserProgramNote(payload: UserProgramNoteDto): Observable<UserProgram> {
    return this.http
      .post<UserProgram>(`${environment.apiUrl}/api/user-program-note`, payload)
      .pipe(catchError(err => this.handleError(err)))
  }

  toggleProgramFavorite(payload: ToggleProgramFavoriteDto): Observable<any> {
    return this.http
      .post<any>(`${environment.apiUrl}/api/toggle-program-favorite`, payload)
      .pipe(catchError(err => this.handleError(err)))
  }

  saveUserProgramPipelineAction(payload: UserProgramPipelineActionDto): Observable<any> {
    return this.http
      .post<any>(`${environment.apiUrl}/api/user-program-pipeline-action`, payload)
      .pipe(catchError(err => this.handleError(err)))
  }

  upgradeAccount(product: string): Observable<UpgradeAccountDto> {
    return this.http
      .post<UpgradeAccountDto>(`${environment.apiUrl}/api/payments/create-checkout-session`, {
        price_id: product,
      })
      .pipe(catchError(err => this.handleError(err)))
  }

  getCustomerInfo(): Observable<CustomerInfoDto> {
    return this.http
      .get<CustomerInfoDto>(`${environment.apiUrl}/api/user-profile`)
      .pipe(catchError(err => this.handleError(err)))
  }

  saveCustomerInfo(payload: CustomerInfoDto): Observable<CustomerInfoDto> {
    return this.http
      .put<CustomerInfoDto>(`${environment.apiUrl}/api/user-profile`, payload)
      .pipe(catchError(err => this.handleError(err)))
  }
}
