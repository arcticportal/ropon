import { Component, HostBinding, inject } from '@angular/core';
import {Location, NgFor, NgIf} from '@angular/common'
import {ActivatedRoute, ActivationStart, Router,
  RouterLink} from '@angular/router'
import {Title} from '@angular/platform-browser'
import {filter, Subscription} from 'rxjs'

import {frontendDomain, Obj, UtilService} from '../util.service'
import {ApiService} from '../api.service'
import {suf} from '../app.routes'
import {MapComponent} from '../map/map.component'

@Component({
  selector: 'app-networks',
  standalone: true,
  imports: [NgFor, NgIf, RouterLink, MapComponent],
  templateUrl: './networks.component.html',
  styleUrl: './networks.component.css'
})
export class NetworksComponent {
  @HostBinding('class.container') container = true
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private title = inject(Title)
  private api = inject(ApiService)
  private popover: any
  location = inject(Location)
  util = inject(UtilService)
  frontendDomain = frontendDomain
  private subscription?: Subscription
  network: any = {}

  ngOnInit() {
    this.api.getNetworks().subscribe(d => {
      this.render(d, this.route)
      this.subscription = this.router.events.pipe(filter(e =>
	e instanceof ActivationStart)).subscribe(e => {
	  this.popover?.hide()
	  this.render(d, e) }) }) }

  ngOnDestroy() {
    this.popover?.hide()
    this.subscription?.unsubscribe() }

  render(d: Obj, e: Obj) {
    var id = e['snapshot'].params['ropon_id']
    if (!id) return
    this.network = d['networks'].find((r: Obj) => r['ropon_id'] == id)
    this.title.setTitle(this.network.name + suf)
    this.popover = new (window as any).bootstrap.Popover(
      document.getElementById('info')) }

  contactHref() {
    var s = this.network?.contact
    return !s ? '' : s.indexOf('@') < 0 ? s : 'mailto:' + s }

  contactText() {
    var s = this.network?.contact
    return !s ? '' : s.indexOf('@') < 0 ? this.util.formatUrl(s) : s }

  modDate() { return (new Date(
    this.network.meta.first_published_at)).toUTCString().slice(5, 16) }
}
