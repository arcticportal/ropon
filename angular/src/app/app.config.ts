import { provideHttpClient } from '@angular/common/http';
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import {
  NgcCookieConsentConfig,
  provideNgcCookieConsent
} from 'ngx-cookieconsent';
import { environment } from '../environments/environment';

import { routes } from './app.routes';

const cookieConfig: NgcCookieConsentConfig = {
  cookie: {domain: environment.frontendDomain},
  palette: {
    popup: {background: '#000'},
    button: {background: '#f1d600'}},
  theme: 'edgeless',
  type: 'opt-out'}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
    provideNgcCookieConsent(cookieConfig)]
};
