import { MAT_DIALOG_DATA } from '@angular/material/dialog'
import { Component, Inject } from '@angular/core'
import { SubmittedDialogData } from '@models/program'

@Component({
  selector: 'app-dialog-submitted',
  templateUrl: 'submitted.dialog.html',
})
export class SubmittedDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: SubmittedDialogData) {}
}
