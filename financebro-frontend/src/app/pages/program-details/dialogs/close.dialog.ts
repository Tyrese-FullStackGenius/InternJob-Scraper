import { MAT_DIALOG_DATA } from '@angular/material/dialog'
import { Component, Inject } from '@angular/core'
import { CloseDialogData } from '@models/program'

export enum ProgramCloseReason {
  accepted = 'ACCEPTED',
  rejected = 'REJECTED',
  cancelled = 'CANCELLED',
  other = 'OTHER',
}

@Component({
  selector: 'app-dialog-close',
  templateUrl: 'close.dialog.html',
})
export class CloseDialogComponent {
  ProgramCloseReason = Object.values(ProgramCloseReason)

  constructor(@Inject(MAT_DIALOG_DATA) public data: CloseDialogData) {}
}
