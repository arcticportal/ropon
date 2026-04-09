import { NgClass, NgFor, NgIf, NgStyle } from '@angular/common';
import { Component, EventEmitter, Output, computed, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { ApiService } from '../api.service';
import { Obj, UtilService } from '../util.service';

@Component({
  selector: 'app-home-filter',
  standalone: true,
  imports: [NgClass, NgFor, NgIf, NgStyle, RouterLink],
  templateUrl: './home-filter.component.html',
  styleUrl: './home-filter.component.css'
})
export class HomeFilterComponent {
  @Output() mobileExpandedChange = new EventEmitter<boolean>()
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private api = inject(ApiService)
  private util = inject(UtilService)
  window = window
  show = false

  filters: Obj = {
    regions: {show: false, list: []},
    subregions: {show: false, list: []},
    domains: {show: false, list: []},
    disciplines: {show: false, list: []},
    asset_types: {show: false, list: []},
    has_catalog: {show: false, list: []}}

  order = [
    {name: 'regions', label: 'Region', options: [
      'Arctic', 'Subarctic', 'Antarctic', 'Southern Ocean', 'Global',
      'Other']},
    {name: 'subregions', label: 'Subregion', options: [
      // Arctic: Land
      'Alaska', 'Canadian Arctic', 'Greenland', 'Iceland', 'Svalbard',
      'Scandinavia', 'Russian Arctic',
      // Arctic: Ocean
      'Sea of Okhotsk', 'Gulf of Alaska', 'Bering Sea', 'Chukchi Sea',
      'Beaufort Sea', 'Canadian Arctic Archipelago', 'Hudson Bay',
      'Labrador Sea', 'Baffin Bay', 'Greenland Sea', 'Norwegian Sea',
      'Barents Sea', 'Kara Sea', 'Laptev Sea', 'East Siberian Sea',
      'Central Arctic Ocean',
      // Subarctic
      'Canadian Subarctic', 'European Subarctic', 'Russian Subarctic',
      // Antarctic: Land
      'Antarctic Peninsula', 'East Antarctica',
      'Transantarctic Mountains', 'West Antarctica',
      'Dronning Maud Land',
      // Southern Oceans
      'Ross Sea', 'Amundsen Sea', 'Bellinghausen Sea', 'Scotia Sea',
      'Weddell Sea', 'East Antarctic Seas',
      // If a network spans too many subregions to delineate separately
      'multiple']},
    {name: 'domains', label: 'Domain', options: [
      'Atmosphere', 'Land', 'Ocean']},
    {name: 'disciplines', label: 'Discipline', options: [
      'Biology', 'Cryosphere', 'Data Management',
      'Education and Outreach', 'Geological Sciences',
      'Instrument Development', 'Meteorology and Climate',
      'Oceanography', 'Social and Human Sciences', 'Space Physics']},
    {name: 'asset_types', label: 'Asset Type', options: [
      'Sites', 'Mobile Platforms', 'Satellites', 'Projects',
      'Campaigns', 'Initiatives']},
    {name: 'has_catalog', label: 'Asset Catalog', options: [
      'Yes', 'No', 'Under Development']}]

  ngOnInit2() {
    var r: Obj = {}
    for (var k in this.filters) {
      this.filters[k].show = this.childSelected(k)
      r[k] = {} }
    this.api.getNetworks().subscribe(nets => {
      var k, v
      for (var d of nets['networks'])
	for (k in r)
	  if (typeof d[k] == 'string') r[k][d[k]] = null
	  else for (v of d[k]) r[k][v] = null
      for (d of this.order) for (v of d.options)
	if (v in r[d.name]) this.filters[d.name].list.push(v) }) }

  ngOnInit() {
    var r: Obj = {}
    for (var k in this.filters) {
      this.filters[k].show = this.childSelected(k)
      r[k] = {} }
    this.api.getList().subscribe(a => {
      var k, v
      for (var d of a['items'])
	for (k in r)
    if (typeof d[k] == 'string') r[k][d[k]] = null
    else if (Array.isArray(d[k]))
      for (v of d[k]) if (v != null) r[k][v] = null
      for (d of this.order) for (v of d.options)
	if (v in r[d.name]) this.filters[d.name].list.push(v)
      //this.updateCount()
    })
    ;(window as any)._res = () => this.api.result }

  qp() { return this.route.snapshot.queryParams }

  caret(k: string) {
    return 'bi-caret-' +
      (this.filters[k].show ? 'down' : 'right') + '-fill' }

  changedQuery(k: string, v: any) {
    return this.util.changedQuery(this.route, k, String(v)) }

  childSelected(k: string) { return this.qp().hasOwnProperty(k) }

  clear() {
    var r: Obj = {}, p = this.qp()
    for (var k in p) r[k] = p[k]
    for (k in this.filters) delete r[k]
    this.router.navigate([], {queryParams: r}) }

  selected(k: string, v: string) { return this.qp()[k] == v }

  styl(k: string, v: any) {
    return !this.selected(k, String(v)) ? {} : {
      'font-weight': 'var(--ropon-bold)'} }

  stylGroup(k: string) {
    return !this.childSelected(k) ? {} : {
      'font-weight': 'var(--ropon-bold)'} }

  stylRadio(k: string, v: any) {
    return 'bi-record' + (this.selected(k, String(v)) ? '2' : '') }

  toggleMobile() {
    this.show = !this.show
    this.mobileExpandedChange.emit(this.show) }

  toggle(k: string) { this.filters[k].show = !this.filters[k].show }

  count = computed(() => {
    var k, v, c: Obj = {}
    for (var d of this.api.result()) for (k in this.filters) {
      if (typeof d[k] == 'string') {
	v = d[k]
	if (!(v in c)) c[v] = 0
	++c[v] }
  else if (Array.isArray(d[k])) for (v of d[k]) {
    if (v == null) continue
	if (!(v in c)) c[v] = 0
	++c[v] } }
    return (k: string) => k in c ? c[k] : 0 })

}
