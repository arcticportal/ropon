import { Injectable, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ActivatedRoute, Params } from '@angular/router';
import { environment } from '../environments/environment';

export const frontendDomain = 'https://'+ environment.frontendDomain
export const backendDomain = environment.backendURL

export const apiPrefix = 'api/v2'
export const useCache = true

export type Obj = {[index: string]: any}

@Injectable({
  providedIn: 'root'
})
export class UtilService {
  private sanitizer = inject(DomSanitizer)

  constructor() { }

  changedQuery(route: ActivatedRoute, k: string, v: string): Params {
    var r: Params = {}, p = route.snapshot.queryParams
    for (var s in p) r[s] = p[s]
    if (!v || k != 'search' && r[k] == v) delete r[k]
    else r[k] = v
    return r }

  formatImg(s: string): string {
    return !s? '' : s.indexOf('http') >= 0 ? s : this.pathJoin('/', s) }

  isUrl(s: string): boolean {
    try { new URL(s); return true }
    catch (_) { return false } }

  formatUrl(s: string | null): string {
    return !s ? '' : s.replace(
      /^https?:\/\/(www\.)?|\/(index\.(html?|php))?$/gi, '') }

  pathJoin(...args: (string | number)[]): string {
    return args.join('///').replace(/\/{3,}/g, '/') }

  sanitise(page: Obj): SafeHtml {
    var r = ['<div class="row"><div class="col-12"><h1>',
	     page['title'], '</h1>']
    for (var d of page['body']) switch (d.type) {
      case 'paragraph': r.push(d.value); break
      case 'heading':
	d = d.value
	r.push('<', d.heading_level, '>', d.heading_text,
	       '</', d.heading_level, '>')
	break
      case 'image':
	d = d.value
	r.push(
	  '</div></div><div class="row justify-content-center">',
	  '<figure class="col-auto" style="aspect-ratio: ',
	  d.width, ' / ', d.height, '"><img src="',
	  this.isUrl(d.url) ? d.url : this.pathJoin(backendDomain, d.url),
	  '" fill class="img-fluid" />',
	  '</figure></div><div class="row"><div class="col-12">')
	break
      default: console.log(`Unknown tag type: ${d.type}`) }
    r.push('</div></div>')
    return this.sanitizer.bypassSecurityTrustHtml(r.join('')) }
}
