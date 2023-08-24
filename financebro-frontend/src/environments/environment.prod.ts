// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
import { Environment } from '@shared/interfaces'

export const environment: Environment = {
  production: true,
  appVersion: 'v8.1.3',
  products: new Map([
    [
      '3months',
      {
        id: 'price_1NNVm1D5UNPd1Scm4AeScWSf',
        name: '3 Months Access',
        price: 49,
      },
    ],
    [
      '6months',
      {
        id: 'price_1NNVm1D5UNPd1ScmucSwF63S',
        name: '6 Months Access',
        price: 79,
      },
    ],
  ]),
  USERDATA_KEY: 'authf649fc9a5f55',
  apiUrl: 'https://backend.opportunify.co.uk',
  appThemeName: 'Opportunify',
  sentryDns: 'https://9c2d7c9b01934753bc65c6787d55b4c1@o4505050793377792.ingest.sentry.io/4505050966065152',
  websiteUrl: 'https://targetopportunities.com',
}

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
