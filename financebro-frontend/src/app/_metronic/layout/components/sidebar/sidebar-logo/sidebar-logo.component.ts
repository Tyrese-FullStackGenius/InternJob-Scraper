import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { LayoutType } from '../../../core/configs/config';
import { LayoutService } from '@app/_metronic/layout';
import {AuthService} from "@app/modules/auth";

@Component({
  selector: 'app-sidebar-logo',
  templateUrl: './sidebar-logo.component.html',
  styleUrls: ['./sidebar-logo.component.scss'],
})
export class SidebarLogoComponent implements OnInit, OnDestroy {
  private unsubscribe: Subscription[] = [];
  @Input() toggleButtonClass: string = '';
  @Input() toggleEnabled: boolean;
  @Input() toggleType: string = '';
  @Input() toggleState: string = '';
  currentLayoutType: LayoutType | null;

  toggleAttr: string;

  get logo(): string {
    if (this.auth.currentUserValue?.email === 'demo.libf@libf.ac.uk')
      return './assets/media/logo-libf.png';
    else if (this.auth.currentUserValue?.email === 'demo.lbs@london.edu')
      return './assets/media/logo-lbs.png';
    else if (this.auth.currentUserValue?.email === 'james.weaver@london.ac.uk')
      return './assets/media/logo-university_of_london.png';
    else
      return './assets/media/opportunity-logo.svg';
  }

  constructor(private layout: LayoutService, public readonly auth: AuthService) {
    console.log()
  }

  ngOnInit(): void {
    this.toggleAttr = `app-sidebar-${this.toggleType}`;
    const layoutSubscr = this.layout.currentLayoutTypeSubject
      .asObservable()
      .subscribe((layout) => {
        this.currentLayoutType = layout;
      });
    this.unsubscribe.push(layoutSubscr);
  }

  ngOnDestroy() {
    this.unsubscribe.forEach((sb) => sb.unsubscribe());
  }
}
