import { Component, HostBinding, inject } from '@angular/core';

import {ApiService} from '../api.service'

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [],
  templateUrl: './about.component.html',
  styleUrl: './about.component.css'
})
export class AboutComponent {
  @HostBinding('class.container') container = true
  private api = inject(ApiService)
  content: any = ''

  constructor() {
    this.api.get('ropon_pages', 6).subscribe(d => {
      this.content = this.api.sanitise(d) }) }
}
