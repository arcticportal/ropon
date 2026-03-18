import { inject, Injectable, signal } from '@angular/core';
import {
  first, forkJoin, map, Observable, of, switchMap,
  tap
} from 'rxjs';

import { CachedHttpService } from './cached-http.service';
import {
  apiPrefix, backendDomain, Obj, useCache,
  UtilService
} from './util.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(CachedHttpService)
  private util = inject(UtilService)
  private db: Obj = {}
  result = signal<Obj[]>([])

  constructor() { }

  get(...args: (string | number)[]): Observable<any> {
    var join = this.util.pathJoin, k = join(...args)
    if (!k.startsWith('https://'))
      k = join(backendDomain, apiPrefix, k)
    return (k in this.db ? of(this.db[k]) :
      this.http.get(k).pipe(
	map((r: any) => {
	  if (r.status != 200) throw new Error(r.statusText)
	  var j
	  try { j = JSON.parse(r.body) }
	  catch (e) { j = {meta: {}, data: r.body} }
	  if (r.headers.has('X-Redirected-From'))
	    j.meta.x_redirected_from = r.headers.get(
	      'X-Redirected-From')
	  console.log(r)
	  return j }),
    	tap(d => { if (useCache) this.db[k] = d }))).pipe(first()) }

  getNetworks(): Observable<Obj> {
    return ('allNetworks' in this.db ? of(this.db['allNetworks']) :
      this.get('networks').pipe(  // FIXME: compare with mergeMap
	switchMap(d => forkJoin(d.items.map((item: Obj) =>
	  this.get('networks', item['id']))).pipe(map(networks =>
	    ({total: d.meta.total_count,
	      items: d.items,
	      networks: networks})))),
	tap(d => { if (useCache) this.db['allNetworks'] = d }))).pipe(
	  first()) }

  getList(): Observable<Obj> {
    return this.get(
      'networks',
      '?fields=logo_image,regions,subregions,domains,disciplines,asset_types,website_url,has_catalog,abbreviation,organization_name&limit=500') }

  getPage(slug: string): Observable<Obj> {
    return this.get('ropon_pages', '?fields=body&slug=' + slug) }
}
