import { Component, HostBinding, inject } from '@angular/core';

import {ApiService} from '../api.service'

@Component({
  selector: 'app-poawg',
  standalone: true,
  imports: [],
  templateUrl: './poawg.component.html',
  styleUrl: './poawg.component.css'
})
export class PoawgComponent {
  @HostBinding('class.container') container = true
  private api = inject(ApiService)
  content: any = ''

  constructor() {
    this.api.get('ropon_pages', 9).subscribe(d => {
      this.content = this.api.sanitise(d) }) }
}
