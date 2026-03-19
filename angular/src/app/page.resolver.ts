import { inject } from '@angular/core'
import { ResolveFn } from '@angular/router'
import { ApiService } from './api.service'

export const pageResolver: ResolveFn<any> = route =>
  inject(ApiService).getPage(route.params['slug'])
