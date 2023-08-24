import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { ThemeModeSwitcherComponent } from './theme-mode-switcher.component';

@NgModule({
  declarations: [ThemeModeSwitcherComponent],
  imports: [CommonModule, InlineSVGModule],
  exports: [ThemeModeSwitcherComponent],
})
export class ThemeModeModule {}
