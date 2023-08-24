import { MAT_DIALOG_DATA } from '@angular/material/dialog'
import { Component, Inject } from '@angular/core'
import { PreRecordedVideoInterviewDialogData } from '@models/program'

@Component({
  selector: 'app-dialog-pre-recorded-video-interview',
  templateUrl: 'pre-recorded-video-interview.dialog.html',
})
export class PreRecordedVideoInterviewDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: PreRecordedVideoInterviewDialogData) {}
}
