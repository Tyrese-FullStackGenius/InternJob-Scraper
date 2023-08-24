import { Component, Input } from '@angular/core';
import {environment} from "@environments/environment";

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss'],
})
export class FooterComponent {
  environment = environment
  @Input() appFooterContainerCSSClass: string = '';

  currentDateStr: string = new Date().getFullYear().toString();
  constructor() {}
}
