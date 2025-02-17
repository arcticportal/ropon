import { Injectable, inject } from '@angular/core';
import {first, forkJoin, map, Observable, of, switchMap,
  tap} from 'rxjs'

import {CachedHttpService} from './cached-http.service'
import {apiPrefix, backendDomain, Obj, useCache,
  UtilService} from './util.service'

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(CachedHttpService)
  private util = inject(UtilService)
  private db: Obj = {}

  constructor() { }

  get(...args: (string | number)[]): Observable<any> {
    var join = this.util.pathJoin, k = join(...args)
    return (k in this.db ? of(this.db[k]) :
      this.http.get(join(backendDomain, apiPrefix, k, '/')).pipe(
    	map(s => JSON.parse(s)),
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
}
