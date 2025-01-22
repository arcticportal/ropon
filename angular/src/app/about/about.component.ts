import { Component, inject } from '@angular/core';

import {Obj} from '../util.service'
import {ApiService} from '../api.service'

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [],
  templateUrl: './about.component.html',
  styleUrl: './about.component.css'
})
export class AboutComponent {
  private api = inject(ApiService)
  window = window
  res: Obj = {}

  constructor() {
    this.api.get('ropon_pages', 7).subscribe((d: Obj) => this.res = d) }
}
