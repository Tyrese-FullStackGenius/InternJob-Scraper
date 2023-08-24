import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { ILayout, LayoutType } from '../../core/configs/config';
import { LayoutService } from '../../core/layout.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
})
export class SidebarComponent implements OnInit, OnDestroy {
  private unsubscribe: Subscription[] = [];

  // public props
  appSidebarDisplay: boolean;
  appSidebarDefaultFixedDesktop: boolean;
  appSidebarDefaultMinimizeDesktopEnabled: boolean;
  appSidebarDefaultMinimizeDesktopDefault: boolean;
  appSidebarDefaultMinimizeDesktopHoverable: boolean;
  appSidebarDefaultMinimizeMobileEnabled: boolean;
  appSidebarDefaultMinimizeMobileDefault: boolean;
  appSidebarDefaultMinimizeMobileHoverable: boolean;
  appSidebarDefaultCollapseDesktopEnabled: boolean;
  appSidebarDefaultCollapseDesktopDefault: boolean;
  appSidebarDefaultCollapseMobileEnabled: boolean;
  appSidebarDefaultCollapseMobileDefault: boolean;

  appSidebarDefaultPushHeader: boolean;
  appSidebarDefaultPushToolbar: boolean;
  appSidebarDefaultPushFooter: boolean;

  appSidebarDefaultStacked: boolean;

  // appSidebarPrimaryStickyAttributes: { [attrName: string]: string } | undefined;

  // appSidebarPrimaryMinimizeDesktopEnabled: boolean;
  // appSidebarPrimaryMinimizeDesktopDefault: boolean;
  // appSidebarPrimaryMinimizeDesktopHoverable: boolean;

  // appSidebarPrimaryMinimizeMobileEnabled: boolean;
  // appSidebarPrimaryMinimizeMobileDefault: boolean;
  // appSidebarPrimaryMinimizeMobileHoverable: boolean;

  // appSidebarPrimaryCollapseDesktopEnabled: boolean;
  // appSidebarPrimaryCollapseDesktopDefault: boolean;

  // appSidebarPrimaryCollapseMobileEnabled: boolean;
  // appSidebarPrimaryCollapseMobileDefault: boolean;

  // appSidebarSecondaryStickyAttributes:
  //   | { [attrName: string]: string }
  //   | undefined;

  // appSidebarSecondaryMinimizeDesktopEnabled: boolean;
  // appSidebarSecondaryMinimizeDesktopDefault: boolean;
  // appSidebarSecondaryMinimizeDesktopHoverable: boolean;

  // appSidebarSecondaryMinimizeMobileEnabled: boolean;
  // appSidebarSecondaryMinimizeMobileDefault: boolean;
  // appSidebarSecondaryMinimizeMobileHoverable: boolean;

  // appSidebarSecondaryCollapseDesktopEnabled: boolean;
  // appSidebarSecondaryCollapseDesktopDefault: boolean;

  // appSidebarSecondaryCollapseMobileEnabled: boolean;
  // appSidebarSecondaryCollapseMobileDefault: boolean;

  // logo
  appSidebarDefaultMinimizeDefault: boolean;
  toggleButtonClass: string;
  toggleEnabled: boolean;
  toggleType: string;
  toggleState: string;

  constructor(private layout: LayoutService) {}

  ngOnInit(): void {
    const subscr = this.layout.layoutConfigSubject
      .asObservable()
      .subscribe((config: ILayout) => {
        this.updateProps(config);
      });
    this.unsubscribe.push(subscr);
  }

  updateProps(config: ILayout) {
    this.appSidebarDisplay = this.layout.getProp('app.sidebar.display', config) as boolean;
    if (!this.appSidebarDisplay) {
      return;
    }

    this.appSidebarDefaultFixedDesktop = this.layout.getProp(
      'app.sidebar.default.fixed.desktop',
      config
    ) as boolean;

    this.appSidebarDefaultMinimizeDesktopEnabled = this.layout.getProp(
      'app.sidebar.default.minimize.desktop.enabled',
      config
    ) as boolean;
    if (this.appSidebarDefaultMinimizeDesktopEnabled) {
      this.appSidebarDefaultMinimizeDesktopDefault = this.layout.getProp(
        'app.sidebar.default.minimize.desktop.default',
        config
      ) as boolean;
      if (this.appSidebarDefaultMinimizeDesktopDefault) {
        document.body.setAttribute('data-kt-app-sidebar-minimize', 'on');
      }

      this.appSidebarDefaultMinimizeDesktopHoverable = this.layout.getProp(
        'app.sidebar.default.minimize.desktop.hoverable',
        config
      ) as boolean;
      if (this.appSidebarDefaultMinimizeDesktopHoverable) {
        document.body.setAttribute('data-kt-app-sidebar-hoverable', 'true');
      }
    }

    this.appSidebarDefaultMinimizeMobileEnabled = this.layout.getProp(
      'app.sidebar.default.minimize.mobile.enabled',
      config
    ) as boolean;
    if (this.appSidebarDefaultMinimizeMobileEnabled) {
      this.appSidebarDefaultMinimizeMobileDefault = this.layout.getProp(
        'app.sidebar.default.minimize.mobile.default',
        config
      ) as boolean;
      if (this.appSidebarDefaultMinimizeMobileDefault) {
        document.body.setAttribute('data-kt-app-sidebar-minimize-mobile', 'on');
      }

      this.appSidebarDefaultMinimizeMobileHoverable = this.layout.getProp(
        'app.sidebar.default.minimize.mobile.hoverable',
        config
      ) as boolean;
      if (this.appSidebarDefaultMinimizeMobileHoverable) {
        document.body.setAttribute(
          'data-kt-app-sidebar-hoverable-mobile',
          'true'
        );
      }
    }

    this.appSidebarDefaultCollapseDesktopEnabled = this.layout.getProp(
      'app.sidebar.default.collapse.desktop.enabled',
      config
    ) as boolean;
    if (this.appSidebarDefaultCollapseDesktopEnabled) {
      this.appSidebarDefaultCollapseDesktopDefault = this.layout.getProp(
        'app.sidebar.default.collapse.desktop.default',
        config
      ) as boolean;
      if (this.appSidebarDefaultCollapseDesktopDefault) {
        document.body.setAttribute('data-kt-app-sidebar-collapse', 'on');
      }
    }

    this.appSidebarDefaultCollapseMobileEnabled = this.layout.getProp(
      'app.sidebar.default.collapse.mobile.enabled',
      config
    ) as boolean;
    if (this.appSidebarDefaultCollapseMobileEnabled) {
      this.appSidebarDefaultCollapseMobileDefault = this.layout.getProp(
        'app.sidebar.default.collapse.mobile.default',
        config
      ) as boolean;
      if (this.appSidebarDefaultCollapseMobileDefault) {
        document.body.setAttribute('data-kt-app-sidebar-collapse-mobile', 'on');
      }
    }

    if (this.layout.getProp('app.sidebar.default.push')) {
      this.appSidebarDefaultPushHeader = this.layout.getProp(
        'app.sidebar.default.push.header',
        config
      ) as boolean;
      if (this.appSidebarDefaultPushHeader) {
        document.body.setAttribute('data-kt-app-sidebar-push-header', 'true');
      }

      this.appSidebarDefaultPushToolbar = this.layout.getProp(
        'app.sidebar.default.push.toolbar',
        config
      ) as boolean;
      if (this.appSidebarDefaultPushToolbar) {
        document.body.setAttribute('data-kt-app-sidebar-push-toolbar', 'true');
      }

      this.appSidebarDefaultPushFooter = this.layout.getProp(
        'app.sidebar.default.push.footer',
        config
      ) as boolean;
      if (this.appSidebarDefaultPushFooter) {
        document.body.setAttribute('data-kt-app-sidebar-push-footer', 'true');
      }
    }

    this.appSidebarDefaultStacked = this.layout.getProp(
      'app.sidebar.default.stacked',
      config
    ) as boolean;
    if (this.appSidebarDefaultStacked) {
      document.body.setAttribute('app-sidebar-stacked', 'true');
    }

    // // Primary sidebar
    // if (this.appSidebarDefaultStacked) {
    //   this.appSidebarPrimaryStickyAttributes = this.layout.getProp(
    //     'app.sidebar.primary.sticky.attributes', config
    //   ) as { [attrName: string]: string } | undefined;
    //   setTimeout(() => {
    //     const appSidebarPrimaryElement = document.getElementById(
    //       'app-sidebar-primary'
    //     );
    //     if (
    //       appSidebarPrimaryElement &&
    //       this.appSidebarPrimaryStickyAttributes
    //     ) {
    //       for (const key in this.appSidebarPrimaryStickyAttributes) {
    //         if (this.appSidebarPrimaryStickyAttributes.hasOwnProperty(key)) {
    //           appSidebarPrimaryElement.setAttribute(
    //             key,
    //             this.appSidebarPrimaryStickyAttributes[key]
    //           );
    //         }
    //       }
    //     }
    //   }, 10);

    //   this.appSidebarPrimaryMinimizeDesktopEnabled = this.layout.getProp(
    //     'app.sidebar.primary.minimize.desktop.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarPrimaryMinimizeDesktopEnabled) {
    //     this.appSidebarPrimaryMinimizeDesktopDefault = this.layout.getProp(
    //       'app.sidebar.primary.minimize.desktop.default', config
    //     ) as boolean;
    //     if (this.appSidebarPrimaryMinimizeDesktopDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-primary-minimize',
    //         'on'
    //       );
    //     }

    //     this.appSidebarPrimaryMinimizeDesktopHoverable = this.layout.getProp(
    //       'app.sidebar.primary.minimize.desktop.hoverable', config
    //     ) as boolean;
    //     if (this.appSidebarPrimaryMinimizeDesktopHoverable) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-primary-hoverable',
    //         'on'
    //       );
    //     }
    //   }

    //   this.appSidebarPrimaryMinimizeMobileEnabled = this.layout.getProp(
    //     'app.sidebar.primary.minimize.mobile.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarPrimaryMinimizeMobileEnabled) {
    //     this.appSidebarPrimaryMinimizeMobileDefault = this.layout.getProp(
    //       'app.sidebar.primary.minimize.mobile.default', config
    //     ) as boolean;
    //     if (this.appSidebarPrimaryMinimizeMobileDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-primary-minimize-mobile',
    //         'on'
    //       );
    //     }

    //     this.appSidebarPrimaryMinimizeMobileHoverable = this.layout.getProp(
    //       'app.sidebar.primary.minimize.mobile.hoverable', config
    //     ) as boolean;
    //     if (this.appSidebarPrimaryMinimizeMobileHoverable) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-primary-hoverable-mobile',
    //         'on'
    //       );
    //     }
    //   }

    //   this.appSidebarPrimaryCollapseDesktopEnabled = this.layout.getProp(
    //     'app.sidebar.primary.collapse.desktop.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarPrimaryCollapseDesktopEnabled) {
    //     this.appSidebarPrimaryCollapseDesktopDefault = this.layout.getProp(
    //       'app.sidebar.primary.collapse.desktop.default', config
    //     ) as boolean;
    //     if (this.appSidebarPrimaryCollapseDesktopDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-primary-collapse',
    //         'on'
    //       );
    //     }
    //   }

    //   this.appSidebarPrimaryCollapseMobileEnabled = this.layout.getProp(
    //     'app.sidebar.primary.collapse.mobile.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarPrimaryCollapseMobileEnabled) {
    //     this.appSidebarPrimaryCollapseMobileDefault = this.layout.getProp(
    //       'app.sidebar.primary.collapse.mobile.default', config
    //     ) as boolean;
    //     if (this.appSidebarPrimaryCollapseMobileDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-primary-collapse-mobile',
    //         'on'
    //       );
    //     }
    //   }
    // }

    // // Secondary sidebar
    // if (this.appSidebarDefaultStacked) {
    //   this.appSidebarSecondaryStickyAttributes = this.layout.getProp(
    //     'app.sidebar.secondary.sticky.attributes', config
    //   ) as { [attrName: string]: string } | undefined;
    //   setTimeout(() => {
    //     const appSidebarSecondaryElement = document.getElementById(
    //       'app-sidebar-secondary'
    //     );
    //     if (
    //       appSidebarSecondaryElement &&
    //       this.appSidebarSecondaryStickyAttributes
    //     ) {
    //       for (const key in this.appSidebarSecondaryStickyAttributes) {
    //         if (this.appSidebarSecondaryStickyAttributes.hasOwnProperty(key)) {
    //           appSidebarSecondaryElement.setAttribute(
    //             key,
    //             this.appSidebarSecondaryStickyAttributes[key]
    //           );
    //         }
    //       }
    //     }
    //   }, 10);

    //   this.appSidebarSecondaryMinimizeDesktopEnabled = this.layout.getProp(
    //     'app.sidebar.secondary.minimize.desktop.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarSecondaryMinimizeDesktopEnabled) {
    //     this.appSidebarSecondaryMinimizeDesktopDefault = this.layout.getProp(
    //       'app.sidebar.secondary.minimize.desktop.default', config
    //     ) as boolean;
    //     if (this.appSidebarSecondaryMinimizeDesktopDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-secondary-minimize',
    //         'on'
    //       );
    //     }

    //     this.appSidebarSecondaryMinimizeDesktopHoverable = this.layout.getProp(
    //       'app.sidebar.secondary.minimize.desktop.hoverable', config
    //     ) as boolean;
    //     if (this.appSidebarSecondaryMinimizeDesktopHoverable) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-secondary-hoverable',
    //         'on'
    //       );
    //     }
    //   }

    //   this.appSidebarSecondaryMinimizeMobileEnabled = this.layout.getProp(
    //     'app.sidebar.secondary.minimize.mobile.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarSecondaryMinimizeMobileEnabled) {
    //     this.appSidebarSecondaryMinimizeMobileDefault = this.layout.getProp(
    //       'app.sidebar.secondary.minimize.mobile.default', config
    //     ) as boolean;
    //     if (this.appSidebarSecondaryMinimizeMobileDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-secondary-minimize-mobile',
    //         'on'
    //       );
    //     }

    //     this.appSidebarSecondaryMinimizeMobileHoverable = this.layout.getProp(
    //       'app.sidebar.secondary.minimize.mobile.hoverable', config
    //     ) as boolean;
    //     if (this.appSidebarSecondaryMinimizeMobileHoverable) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-secondary-hoverable-mobile',
    //         'on'
    //       );
    //     }
    //   }

    //   this.appSidebarSecondaryCollapseDesktopEnabled = this.layout.getProp(
    //     'app.sidebar.secondary.collapse.desktop.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarSecondaryCollapseDesktopEnabled) {
    //     this.appSidebarSecondaryCollapseDesktopDefault = this.layout.getProp(
    //       'app.sidebar.secondary.collapse.desktop.default', config
    //     ) as boolean;
    //     if (this.appSidebarSecondaryCollapseDesktopDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-secondary-collapse',
    //         'on'
    //       );
    //     }
    //   }

    //   this.appSidebarSecondaryCollapseMobileEnabled = this.layout.getProp(
    //     'app.sidebar.secondary.collapse.mobile.enabled', config
    //   ) as boolean;
    //   if (this.appSidebarSecondaryCollapseMobileEnabled) {
    //     this.appSidebarSecondaryCollapseMobileDefault = this.layout.getProp(
    //       'app.sidebar.secondary.collapse.mobile.default', config
    //     ) as boolean;
    //     if (this.appSidebarSecondaryCollapseMobileDefault) {
    //       document.body.setAttribute(
    //         'data-kt-app-sidebar-secondary-collapse-mobile',
    //         'on'
    //       );
    //     }
    //   }
    // }

    // Logo
    this.appSidebarDefaultMinimizeDefault = this.layout.getProp(
      'app.sidebar.default.minimize.default',
      config
    ) as boolean;
    this.toggleButtonClass = this.appSidebarDefaultMinimizeDefault
      ? 'active'
      : '';
    this.toggleEnabled =
      this.appSidebarDefaultMinimizeDesktopEnabled ||
      this.appSidebarDefaultCollapseDesktopEnabled;
    if (this.appSidebarDefaultMinimizeDesktopEnabled) {
      this.toggleType = 'minimize';
      this.toggleState = 'active';
    }

    if (this.appSidebarDefaultCollapseDesktopEnabled) {
      this.toggleType = 'collapse';
      this.toggleState = '';
    }

    document.body.setAttribute('data-kt-app-sidebar-enabled', 'true');
    document.body.setAttribute(
      'data-kt-app-sidebar-fixed',
      this.appSidebarDefaultFixedDesktop.toString()
    );
  }

  ngOnDestroy() {
    this.unsubscribe.forEach((sb) => sb.unsubscribe());
  }
}
