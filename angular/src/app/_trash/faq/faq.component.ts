import { Component, HostBinding, inject } from '@angular/core';

import {ApiService} from '../api.service'

@Component({
  selector: 'app-faq',
  standalone: true,
  imports: [],
  templateUrl: './faq.component.html',
  styleUrl: './faq.component.css'
})
export class FaqComponent {
  @HostBinding('class.container') container = true
  private api = inject(ApiService)
  content: any = ''

  constructor() {
    this.api.get('ropon_pages', 10).subscribe(d => {
      this.content = this.api.sanitise(d) }) }
}
