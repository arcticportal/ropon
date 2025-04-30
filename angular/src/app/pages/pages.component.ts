import { Component, HostBinding, inject } from '@angular/core';
import {ActivatedRoute, ActivationStart, Router} from '@angular/router'
import {Title} from '@angular/platform-browser'
import {filter, Subscription, switchMap} from 'rxjs'

import {ApiService} from '../api.service'
import {Obj, UtilService} from '../util.service'
import {suf} from '../app.routes'

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
  private router = inject(Router)
  private title = inject(Title)
  private api = inject(ApiService)
  private util = inject(UtilService)
  private subscription?: Subscription
  content: any = ''

  ngOnInit2() {
    this.api.get('ropon_pages').subscribe(d => {
      this.render(d, this.route)
      this.subscription = this.router.events.pipe(filter(e =>
	e instanceof ActivationStart)).subscribe(e => {
	  this.render(d, e) }) }) }

  ngOnInit() {
    this.api.getPage(this.route.snapshot.params['slug']).subscribe(d =>{
      this.render2(d)
      this.subscription = this.router.events.pipe(
	filter(e =>e instanceof ActivationStart),
	switchMap(e => this.api.getPage(e.snapshot.params['slug']))
      ).subscribe(d => { this.render2(d) }) }) }

  ngOnDestroy() {
    this.subscription?.unsubscribe() }

  render(d: Obj, e: Obj) {
    var slug = e['snapshot'].params['slug']
    d = d['items'].find((r: Obj) => r['meta'].slug == slug)
    if (!d) {
      this.content = '<h1>404</h1>'
      this.title.setTitle('404' + suf)
      return }
    this.api.get('ropon_pages', d['id']).subscribe(p => {
      this.content = this.util.sanitise(p) })
    this.title.setTitle(d['title'] + suf) }

  render2(d: Obj) {
    if (!d['items'].length) {
      this.content = '<h1>404</h1>'
      this.title.setTitle('404' + suf)
      return }
    d = d['items'][0]
    this.content = this.util.sanitise(d)
    this.title.setTitle(d['title'] + suf) }
}
