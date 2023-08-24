import {Component, OnInit} from '@angular/core';
import { environment } from '@environments/environment';

@Component({
  selector: 'app-explore-main-drawer',
  templateUrl: './explore-main-drawer.component.html',
})
export class ExploreMainDrawerComponent implements OnInit {
  appThemeName: string = environment.appThemeName;

  constructor() {
  }

  ngOnInit(): void {
  }
}
