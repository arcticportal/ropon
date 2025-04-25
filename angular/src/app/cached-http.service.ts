import { Injectable, inject } from '@angular/core';
import {HttpClient, HttpResponse} from '@angular/common/http'
import {Observable, of, tap} from 'rxjs'

import {useCache} from './util.service'

var cache: {[index: string]: any} = {}

@Injectable({
  providedIn: 'root'
})
export class CachedHttpService {
  private http = inject(HttpClient)

  constructor() { }

  get(url: string): Observable<HttpResponse<any>> {
    return url in cache ? of(cache[url]) :
      this.http.get(url, {
	observe: 'response', responseType: 'text'}).pipe(
    	  tap(r => { if (useCache) cache[url] = r })) }
}
