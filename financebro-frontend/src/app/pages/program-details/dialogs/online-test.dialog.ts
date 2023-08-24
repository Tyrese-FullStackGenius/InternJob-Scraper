import { MAT_DIALOG_DATA } from '@angular/material/dialog'
import { Component, Inject } from '@angular/core'
import { OnlineTestDialogData } from '@models/program'

@Component({
  selector: 'app-dialog-online-test',
  templateUrl: 'online-test.dialog.html',
})
export class OnlineTestDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: OnlineTestDialogData) {}
}
