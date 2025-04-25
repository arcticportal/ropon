import { Component, HostListener, inject } from '@angular/core';
import {NgStyle} from '@angular/common'
import {
  ActivatedRoute, NavigationStart, Router,
  RouterLink} from '@angular/router'
import {Subscription} from 'rxjs'
import {filter} from 'rxjs/operators'

function getY(): number { return Math.round(
  window.scrollY || window.pageYOffset ||
  document.documentElement.scrollTop || document.body.scrollTop || 0) }

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [NgStyle, RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private resizeTimeout: any
  private width = window.outerWidth
  private prevId = 'DUMMY'
  private scrollLock = false
  private subscription?: Subscription

  ngOnInit() {
    //this.router.events.subscribe(e => { console.log(e) })
    this.subscription = this.router.events.pipe(filter(e =>
      e instanceof NavigationStart)).subscribe((e: NavigationStart) => {
	if (this.scrollLock) return
	this.scrollLock = true
	var id = this.id(e)
	if (id == this.prevId) { this.scrollLock = false; return }
	this.prevId = id
	var y = 0
	if (e.navigationTrigger == 'popstate' && e.restoredState) {
	  y = Number(sessionStorage.getItem(id))
	  if (isNaN(y)) y = 0 }
	//console.log('Scrolling in', id, 'to', y)
	setTimeout(() => {
	  window.scrollTo({top: y, behavior: 'auto'})
	  this.scrollLock = false }, 10) }) }

  ngOnDestroy() { this.subscription?.unsubscribe() }

  id(e?: NavigationStart): string {
    var a = (e || (this.route.snapshot as
	  any)._routerState).url.slice(1).split('/'),
	r = a.length ? a[0].replace(/\?.*$/, '') : ''
    if (!r) r = 'home'
    if (['networks', 'ropon-pages'].includes(r))
      r = a[1].replace(/\?.*$/, '')
    return r }
    
  styl(s: string): {[index: string]: string} {
    return this.id() != s ? {} : {
      'font-weight': 'var(--ropon-bold)',
      'text-decoration': 'underline'} }

  logoPath(): string {
    return this.width > 991.98 ? '/ropon-text.png' : '/ropon.png' }

  setY(k: string): void {
    var y = getY()
    //console.log('Setting', k, 'to', y)
    sessionStorage.setItem(k, String(y)) }

  @HostListener('window:resize')
  onWindowResize(): void {
    if (this.resizeTimeout) clearTimeout(this.resizeTimeout)
    this.resizeTimeout = setTimeout(
      (() => { this.width = window.outerWidth }).bind(this), 100) }

  @HostListener('window:scroll', [])
  onWindowScroll(): void {
    if (!this.scrollLock && this.id() == this.prevId)
      this.setY(this.prevId) }
}
