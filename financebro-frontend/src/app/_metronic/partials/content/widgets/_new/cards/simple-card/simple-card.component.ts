import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-simple-card',
  templateUrl: './simple-card.component.html',
  styleUrls: ['./simple-card.component.scss'],
})
export class SimpleCardComponent implements OnInit {
  @Input() cssClass: string = '';
  @Input() title: string = 'Summer';
  @Input() description: string = 'Open Internships ';
  @Input() stats: number = 30;

  constructor() {}

  ngOnInit(): void {}
}
