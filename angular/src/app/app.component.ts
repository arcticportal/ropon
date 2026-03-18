import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';

import { NgcCookieConsentService } from 'ngx-cookieconsent';

import { GdprService } from './gdpr.service';

import { FooterComponent } from './footer/footer.component';
import { HeaderComponent } from './header/header.component';

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
  private router = inject(Router)
  private statusChangeSubscription!: Subscription
  private routerSubscription!: Subscription

  title = 'ropon';

  ngOnInit() {
    var c = this.ccService
    this.gdpr.gaLoad()

    this.statusChangeSubscription = c.statusChange$.subscribe(event => {
      if (event.status == 'allow') this.gdpr.gaAllow()
      else this.gdpr.gaDeny() })

    if (c.hasConsented()) this.gdpr.gaAllow()
    else if (c.hasAnswered()) this.gdpr.gaDeny()

    this.routerSubscription = this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe(e => {
      this.gdpr.trackPageView(
        (e as NavigationEnd).urlAfterRedirects,
        document.title) }) }

  ngOnDestroy() {
    this.statusChangeSubscription.unsubscribe()
    this.routerSubscription.unsubscribe() }
}
