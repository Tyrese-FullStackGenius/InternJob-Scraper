import { ChangeDetectionStrategy, Component, HostBinding, Input } from '@angular/core'

@Component({
  selector: 'app-content-reduce-view',
  templateUrl: './content-reduce-view.component.html',
  styleUrls: ['./content-reduce-view.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContentReduceViewComponent {
  @Input() imagesView = false
  @Input() items: Array<string> = []
  @Input() visible = 3
  @HostBinding('class') get class() {
    return this.fullView ? '' : 'reduceView'
  }

  fullView = false

  get reduceView(): boolean {
    return this.items.length > this.visible
  }

  showJoined(items: Array<string>): string {
    return items.join(', ')
  }

  showFullView() {
    this.fullView = true
  }
}
