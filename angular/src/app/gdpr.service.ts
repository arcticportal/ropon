import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';

function gtag(...a: any[]) { (window as any).dataLayer.push(a) }

function deleteCookies(domain: string, ...prefixes: string[]) {
  for (var c of document.cookie.split('; ')) {
    c = c.split('=')[0].trim()
    if (prefixes.some(p => c.startsWith(p)))
      document.cookie = [
	c + '=',
	'Expires=Thu, 01 Jan 1970 00:00:00 GMT',
	'Max-Age=0',
	'Path=/',
	`Domain=${environment.frontendDomain};`].join('; ') } }

const gtagId = environment.googleTagId || 'G-K3ZYKQZDFB';

@Injectable({
  providedIn: 'root'
})
export class GdprService {
  private consented = false

  constructor() { }

  gaLoad() {
    var w = window as any
    w.dataLayer = w.dataLayer || []
    gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied' })
    var s = document.createElement('script')
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + gtagId
    s.async = true
    document.head.appendChild(s)
    gtag('js', new Date())
    gtag('config', gtagId, { send_page_view: false }) }

  gaAllow() {
    this.consented = true
    ;(window as any)['ga-disable-' + gtagId] = false
    gtag('consent', 'update', {
      ad_storage: 'granted',
      ad_user_data: 'granted',
      ad_personalization: 'granted',
      analytics_storage: 'granted' })
    gtag('event', 'page_view', {
      page_path: window.location.pathname,
      page_title: document.title }) }

  gaDeny() {
    this.consented = false
    deleteCookies(environment.frontendDomain, '_ga', '_gid')
    gtag('consent', 'update', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied' })
    ;(window as any)['ga-disable-' + gtagId] = true }

  trackPageView(url: string, title: string) {
    if (this.consented)
      gtag('event', 'page_view', {
        page_path: url,
        page_title: title }) }
}
