import { Component, HostBinding, inject } from '@angular/core';
import {ActivatedRoute} from '@angular/router'

import {Obj, UtilService} from '../util.service'

@Component({
  selector: 'app-pages',
  standalone: true,
  imports: [],
  templateUrl: './pages.component.html',
  styleUrl: './pages.component.css'
})
export class PagesComponent {
  @HostBinding('class.container') container = true
  private route = inject(ActivatedRoute)
  private util = inject(UtilService)
  content: any = ''

  ngOnInit() {
    this.route.data.subscribe(d => {
      this.render2(d['page'])
    }) }

  render2(d: Obj) {
    if (!d['items'].length) {
      this.content = '<h1>404</h1>'
      return }
    d = d['items'][0]
    this.content = this.util.sanitise(d) }
}
