import { Component, OnInit } from '@angular/core';
import {AuthService} from "@app/modules/auth";

@Component({
  selector: 'app-sidebar-menu',
  templateUrl: './sidebar-menu.component.html',
  styleUrls: ['./sidebar-menu.component.scss']
})
export class SidebarMenuComponent implements OnInit {

  constructor(public readonly authService: AuthService) { }

  ngOnInit(): void {

  }

}
