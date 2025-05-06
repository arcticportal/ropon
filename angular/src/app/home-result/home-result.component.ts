import { Component, HostListener, inject } from '@angular/core';
import {NgFor, NgIf} from '@angular/common'
import {ActivatedRoute, Params, RouterLink} from '@angular/router'

import {Obj, UtilService} from '../util.service'
import {ApiService} from '../api.service'

function matchSearch(d: Params, s: string): boolean {
  var k, v
  s = s.toLowerCase()
  function f(d: Params): boolean {
    for (k in d) {
      v = d[k]
      if (typeof v == 'number') v = v.toString()
      if (typeof v == 'string') {
	if (v.toLowerCase().search(s) >= 0) return true }
      else if (typeof v == 'object') if (f(v)) return true }
    return false }
  return f(d) }

function match(d: Params, k: string, v: any): boolean {
  return k == 'search' ? matchSearch(d, v) :
    typeof d[k] == 'object' ? d[k].includes(v) : d[k] == v }

function filtered(a: Obj[], p: Params): Obj[] {
  var k
  return a.filter(d => {
    for (k in p)
      if (k == 'search') { if (!matchSearch(d, p[k])) return false }
      else if (!match(d, k, p[k])) return false
    return true }) }

@Component({
  selector: 'app-home-result',
  standalone: true,
  imports: [NgFor, NgIf, RouterLink],
  templateUrl: './home-result.component.html',
  styleUrl: './home-result.component.css'
})
export class HomeResultComponent {
  private route = inject(ActivatedRoute)
  private api = inject(ApiService)
  private resizeTimeout: any
  width = window.outerWidth
  util = inject(UtilService)
  total: number = 0
  all: Obj[] = []
  networks: any[] = []

  ngOnInit2() {
    this.api.getNetworks().subscribe(d => {
      this.total = d['total'],
      this.all = d['networks'].toSorted((a: Obj, b: Obj) => {
	var s = a['name'].toLowerCase(), t = b['name'].toLowerCase()
	return s < t ? -1 : s > t ? 1 : 0 })
      this.networks = filtered(
	this.all, this.route.snapshot.queryParams) })
    this.route.queryParams.subscribe(p => {
      this.networks = filtered(this.all, p) }) }

  ngOnInit() {
    this.api.getList().subscribe(d => {
      this.total = d['meta'].total_count,
      this.all = d['items'].toSorted((a: Obj, b: Obj) => {
	var s = a['title'].toLowerCase(), t = b['title'].toLowerCase()
	return s < t ? -1 : s > t ? 1 : 0 })
      this.networks = filtered(
	this.all, this.route.snapshot.queryParams) })
    this.route.queryParams.subscribe(p => {
      this.networks = filtered(this.all, p) }) }

  count(): string {
    if (!this.total) return ''
    var r = [], n = this.networks.length
    if (this.total != n) r.push(n, 'found in')
    r.push(this.total, 'total')
    return r.join(' ') }

  @HostListener('window:resize')
  onWindowResize(): void {
    if (this.resizeTimeout) clearTimeout(this.resizeTimeout)
    this.resizeTimeout = setTimeout(
      (() => { this.width = window.outerWidth }).bind(this), 100) }
}
