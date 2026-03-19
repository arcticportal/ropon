import { inject } from '@angular/core'
import { ResolveFn } from '@angular/router'
import { ApiService } from './api.service'

export const networkResolver: ResolveFn<any> = route =>
  inject(ApiService).get('networks', route.params['ropon_id'], '')
