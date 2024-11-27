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
