import { Component, HostBinding, inject } from '@angular/core';
import {Location, NgFor, NgIf} from '@angular/common'
import {HttpClient} from '@angular/common/http'
import {ActivatedRoute, ActivationStart, Router,
  RouterLink} from '@angular/router'
import {Title} from '@angular/platform-browser'
import {filter, first, map, Subscription, switchMap} from 'rxjs'

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
  private http = inject(HttpClient)
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
  showBookmarkMessage = false
  all: Obj[] = []

  navigate(s: string) {
    this.router.navigateByUrl(s, {replaceUrl: true}) }

  ngOnInit2() {
    this.api.getNetworks().subscribe(d => {
      this.render(d, this.route)
      this.subscription = this.router.events.pipe(filter(e =>
	e instanceof ActivationStart)).subscribe(e => {
	  //this.popover?.hide()
	  this.render(d, e) }) }) }

  ngOnInit() {
    this.api.get('networks', this.route.snapshot.params[
      'ropon_id'], '').subscribe(d => {
	this.network = d
	this.title.setTitle(d.name + suf)
	this.subscription = this.router.events.pipe(
	  filter(e => e instanceof ActivationStart),
	  map(e => e.snapshot.params['ropon_id']),
	  switchMap(id => this.api.get('networks', id, ''))).subscribe(
	    d => {
	      this.network = d
	      this.title.setTitle(d.name + suf) }) })
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

  ngOnDestroy() {
    //this.popover?.hide()
    this.subscription?.unsubscribe() }

  render(d: Obj, e: Obj) {
    var id = e['snapshot'].params['ropon_id']
    if (!id) return
    //this.checkOldId(id)
    this.network = d['networks'].find((r: Obj) => r['ropon_id'] == id)
    /*this.popover = new (window as any).bootstrap.Popover(
      document.getElementById('info'))*/
    this.title.setTitle(this.network.name + suf) }

  render2(d: Obj, e: Obj) {
    var id = e['snapshot'].params['ropon_id']
    if (!id) return
    this.network = d
    this.title.setTitle(this.network.name + suf) }

  checkOldId(id: string) {
    this.api.get(this.frontendDomain, 'network', id).pipe(
      first()).subscribe(d => {
	this.showBookmarkMessage = 'x_redirected_from' in d.meta
	console.log(d)
	if (this.showBookmarkMessage) console.log('gets here')
      }) }

  contactHref() {
    var s = this.network?.contact
    return !s ? '' : s.indexOf('@') < 0 ? s : 'mailto:' + s }

  contactText() {
    var s = this.network?.contact
    return !s ? '' : s.indexOf('@') < 0 ? this.util.formatUrl(s) : s }

  modDate() { return (new Date(
    this.network.meta.date_last_modified)).toUTCString().slice(5, 16) }
}
