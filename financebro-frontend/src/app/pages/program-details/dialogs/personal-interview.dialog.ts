import { MAT_DIALOG_DATA } from '@angular/material/dialog'
import { Component, Inject } from '@angular/core'
import { PersonalInterviewDialogData } from '@models/program'

@Component({
  selector: 'app-dialog-personal-interview',
  templateUrl: 'personal-interview.dialog.html',
})
export class PersonalInterviewDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: PersonalInterviewDialogData) {}
}
