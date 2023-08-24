import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core'
import { ActivatedRoute } from '@angular/router'
import {
  CommunityReportedData,
  DialogInitData,
  ProgramActions,
  UserProgram,
  UserProgramPipelineActionDto,
} from '@models/program'
import { FormGroup, NgForm, NonNullableFormBuilder, Validators } from '@angular/forms'
import { ApiService } from '@shared/services/api.service'
import { filter, finalize, switchMap, tap } from 'rxjs/operators'
import { fromEvent, Subscription } from 'rxjs'
import { MatDialog } from '@angular/material/dialog'
import { ComponentType } from '@angular/cdk/overlay'
import { OnlineTestDialogComponent } from '@pages/program-details/dialogs/online-test.dialog'
import { SubmittedDialogComponent } from '@pages/program-details/dialogs/submitted.dialog'
import { PreRecordedVideoInterviewDialogComponent } from '@pages/program-details/dialogs/pre-recorded-video-interview.dialog'
import { PersonalInterviewDialogComponent } from '@pages/program-details/dialogs/personal-interview.dialog'
import { CloseDialogComponent } from '@pages/program-details/dialogs/close.dialog'
import { CommonService } from '@shared/services/common.service'

@Component({
  selector: 'app-program-details',
  templateUrl: './program-details.component.html',
  styleUrls: ['./program-details.component.scss'],
})
export class ProgramDetailsComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('formEl') private formEl: ElementRef
  @ViewChild('formDirective') private formDirective: NgForm

  private readonly dialogDataMap = new Map<
    string,
    DialogInitData<
      | SubmittedDialogComponent
      | OnlineTestDialogComponent
      | PreRecordedVideoInterviewDialogComponent
      | PersonalInterviewDialogComponent
      | CloseDialogComponent
    >
  >([
    [
      'is_application_submitted',
      {
        action: 'submitted',
        component: SubmittedDialogComponent,
        data: { does_ask_for_cover_letter: false },
      },
    ],
    [
      'is_online_test_taken',
      {
        action: 'online_test',
        component: OnlineTestDialogComponent,
        data: { online_test_questions: '' },
      },
    ],
    [
      'is_pre_recorded_video_interview_taken',
      {
        action: 'pre_recorded_video_interview',
        component: PreRecordedVideoInterviewDialogComponent,
        data: { was_there_no_online_test: false, pre_recorded_video_interview_format: '' },
      },
    ],
    [
      'is_personal_interview_taken',
      {
        action: 'personal_interview',
        component: PersonalInterviewDialogComponent,
        data: {
          was_there_no_online_test: false,
          was_there_no_pre_recorded_video_interview_stage: false,
          personal_interview_questions: '',
        },
      },
    ],
    [
      'is_application_closed',
      {
        action: 'close',
        component: CloseDialogComponent,
        data: { application_close_reason: '' },
      },
    ],
  ])

  communityReportedData: CommunityReportedData
  communityReportedDataQuestions = new Map<
    'online_test_questions' | 'pre_recorded_video_interview_format' | 'personal_interview_questions',
    string
  >([
    ['online_test_questions', 'Online Test Format'],
    ['pre_recorded_video_interview_format', 'Video Interview Questions'],
    ['personal_interview_questions', 'Final Interview Questions'],
  ])
  formNote: FormGroup
  form: FormGroup
  formInitialized = false
  loading = true
  program: UserProgram
  programId: number
  saving = false
  subscribers: Subscription[] = []

  constructor(
    private readonly route: ActivatedRoute,
    private fb: NonNullableFormBuilder,
    public apiService: ApiService,
    public dialog: MatDialog,
    public commonService: CommonService,
  ) {
    this.programId = Number(route.snapshot.params.id)

    this.formNote = fb.group({
      note: ['', [Validators.required]],
    })

    // Create form
    let controls = {}
    for (let control of this.dialogDataMap.keys()) {
      controls = { ...controls, [control]: [false] }
    }
    this.form = this.fb.group(controls)

    // Observe form controls changes
    Object.keys(this.form.controls).forEach(key => {
      this.form.controls[key].valueChanges.subscribe(value => {
        if (this.formInitialized) {
          const action = this.dialogDataMap.get(key)!.action
          if (value) {
            this.openDialog(action, this.dialogDataMap.get(key)!.data, this.dialogDataMap.get(key)!.component)
          } else {
            this.apiService
              .saveUserProgramPipelineAction({
                action,
                optional_info: {},
                program_id: this.programId,
                value: false,
              })
              .subscribe()
          }
          // this.form.controls[key].disable({ emitEvent: false })
        }
      })
    })
  }

  ngOnInit() {
    this.apiService
      .getProgram(this.programId)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe(program => {
        this.program = program
        // Re-init form when program details are known
        Object.keys(this.form.controls).forEach(key => {
          const value = this.program[key as keyof UserProgram]
          const control = this.form.controls[key]
          control.patchValue(value)
          // control[value ? 'disable' : 'enable']()
        })
        this.formInitialized = true
      })

    this.apiService.getProgramCommunityReportedData(this.programId).subscribe(({ community_reported_data }) => {
      this.communityReportedData = community_reported_data
    })
  }

  ngAfterViewInit() {
    fromEvent(this.formEl.nativeElement, 'submit')
      .pipe(
        filter(() => {
          this.formNote.markAllAsTouched()
          return this.formNote.valid
        }),
        tap(() => (this.saving = true)),
        switchMap(() =>
          this.apiService
            .saveUserProgramNote({ program_id: this.programId, note: this.formNote.get('note')?.value })
            .pipe(
              finalize(() => {
                this.saving = false
                this.formNote.reset()
                this.formDirective.resetForm()
              }),
            ),
        ),
      )
      .subscribe(program => (this.program = program))
  }

  openDialog<T>(action: ProgramActions, data: any, dialogComponent: ComponentType<T>) {
    const dialogRef = this.dialog.open(dialogComponent, { data })
    dialogRef
      .afterClosed()
      .pipe(
        switchMap((optional_info: UserProgramPipelineActionDto) =>
          this.apiService.saveUserProgramPipelineAction({
            action,
            optional_info: optional_info ?? {},
            program_id: this.programId,
            value: true,
          }),
        ),
      )
      .subscribe()
  }

  ngOnDestroy() {
    this.subscribers.forEach(s => s.unsubscribe())
  }
}
