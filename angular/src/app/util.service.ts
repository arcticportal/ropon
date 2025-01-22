import { Injectable, inject } from '@angular/core';

export const backendPrefix = 'https://wagtail.ropon.dev.cntb.arcticportal.org/api/v2/'
export const useCache = true

export type Obj = {[index: string]: any}

@Injectable({
  providedIn: 'root'
})
export class UtilService {

  constructor() { }
}
