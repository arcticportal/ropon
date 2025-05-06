import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {Subscription} from 'rxjs'

import {NgcCookieConsentService} from 'ngx-cookieconsent'

import {CookieConsentService} from './cookie-consent.service'
import {GdprService} from './gdpr.service'

import {HeaderComponent} from './header/header.component'
import {FooterComponent} from './footer/footer.component'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit, OnDestroy {
  private ccService = inject(NgcCookieConsentService)
  private gdpr = inject(GdprService)
  private statusChangeSubscription!: Subscription

  title = 'ropon';

  ngOnInit() {
    var c = this.ccService
    this.gdpr.gaLoad()

    this.statusChangeSubscription = c.statusChange$.subscribe(event => {
      // FIXME: load first if not already
      if (event.status == 'allow') this.gdpr.gaAllow()
      else this.gdpr.gaDeny() }) }

  ngOnDestroy() {
    this.statusChangeSubscription.unsubscribe() }
}
