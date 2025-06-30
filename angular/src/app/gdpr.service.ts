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

  constructor() { }

  gaLoad() {
    // look at als/src/app/gdpr.service.ts
    var w = window as any
    w.dataLayer = w.dataLayer || []
    gtag('js', new Date())
    gtag('config', gtagId) }

  gaAllow() {
    (window as any)['ga-disable-' + gtagId] = false
    gtag('consent', 'update', {
      ad_storage: 'granted', analytics_storage: 'granted'})
    gtag('event', 'page_view') }

  gaDeny() {
    deleteCookies(environment.frontendDomain, '_ga', '_gid')
    gtag('consent', 'update', {
      ad_storage: 'denied', analytics_storage: 'denied'})
    ;(window as any)['ga-disable-' + gtagId] = true }
}
