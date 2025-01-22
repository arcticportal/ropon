import { Injectable, inject } from '@angular/core';
import {map, of, tap, zip} from 'rxjs'

import {CachedHttpService} from './cached-http.service'
import {backendPrefix, Obj, useCache} from './util.service'

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private http = inject(CachedHttpService)
  private db: Obj = {}

  constructor() { }

  get(typ: string, id: number) {
    var k = `${typ}/${id}`
    return k in this.db ? of(this.db[k]) :
      this.http.get(`${backendPrefix}${k}`).pipe(
    	map((s: string) => JSON.parse(s)),
    	tap(d => { if (useCache) this.db[k] = d })) }
}
