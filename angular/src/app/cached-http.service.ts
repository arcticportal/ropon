import { Injectable, inject } from '@angular/core';
import {HttpClient} from '@angular/common/http'
import {Observable, of, tap} from 'rxjs'

import {useCache} from './util.service'

var cache: {[index: string]: string} = {}

@Injectable({
  providedIn: 'root'
})
export class CachedHttpService {
  private http = inject(HttpClient)

  constructor() { }

  get(url: string): Observable<string> {
    return url in cache ? of(cache[url]) :
      this.http.get(url, {responseType: 'text'}).pipe(
    	tap(s => { if (useCache) cache[url] = s })) }
}
