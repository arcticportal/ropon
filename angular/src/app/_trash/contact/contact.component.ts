import { Component, HostBinding, inject } from '@angular/core';

import {ApiService} from '../api.service'

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.css'
})
export class ContactComponent {
  @HostBinding('class.container') container = true
  private api = inject(ApiService)
  content: any = ''

  constructor() {
    this.api.get('ropon_pages', 8).subscribe(d => {
      this.content = this.api.sanitise(d) }) }
}
