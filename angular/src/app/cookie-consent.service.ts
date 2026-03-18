// UNUSED: This service is not referenced anywhere in the app.
// Consent management is handled by ngx-cookieconsent (in app.config.ts) and GdprService.
// Will be removed in a future cleanup.
import { Injectable, inject } from '@angular/core';
import {HttpClient} from '@angular/common/http'
import {Observable} from 'rxjs'

@Injectable({
  providedIn: 'root'
})
export class CookieConsentService {
  private http = inject(HttpClient)

  constructor() { }

  getConsentStatus(): Observable<any> {
    return this.http.get('/api/gdpr/status') }
}
