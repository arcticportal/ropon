import { Location, NgFor, NgIf } from '@angular/common';
import { Component, HostBinding, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { ApiService } from '../api.service';
import { MapComponent } from '../map/map.component';
import { frontendDomain, Obj, UtilService } from '../util.service';

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
  private api = inject(ApiService)
  private popover: any
  location = inject(Location)
  util = inject(UtilService)
  frontendDomain = frontendDomain
  network: any = {}
  showBookmarkMessage = false
  all: Obj[] = []

  navigate(s: string) {
    this.router.navigateByUrl(s, {replaceUrl: true}) }

  ngOnInit() {
    this.route.data.subscribe(d => {
      this.network = d['network']
    })
    this.api.getList().subscribe(d => {
      this.all = d['items'].toSorted((a: Obj, b: Obj) => {
	var s = a['name'].toLowerCase(), t = b['name'].toLowerCase()
	return s < t ? -1 : s > t ? 1 : 0 }) }) }

  prev() {
    var i = this.all.findIndex((r: Obj) =>
      r['ropon_id'] == this.route.snapshot.params['ropon_id'])
    return i > 0 ? i - 1 : -1 }

  next() {
    var i = this.all.findIndex((r: Obj) =>
      r['ropon_id'] == this.route.snapshot.params['ropon_id'])
    return i >= 0 && i < this.all.length - 1 ? i + 1 : -1 }

  contactHref() {
    var s = this.network?.contact
    return !s ? '' : s.indexOf('@') < 0 ? s : 'mailto:' + s }

  contactText() {
    var s = this.network?.contact
    return !s ? '' : s.indexOf('@') < 0 ? this.util.formatUrl(s) : s }

  modDate() { return (new Date(
    this.network.meta.date_last_modified)).toUTCString().slice(5, 16) }
}
