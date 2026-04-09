import { NgOptimizedImage } from '@angular/common';
import {
  Component, HostBinding, HostListener, inject, ViewChild
} from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { debounceTime } from 'rxjs/operators';

import { ApiService } from '../api.service';
import { HomeFilterComponent } from '../home-filter/home-filter.component';
import { HomeResultComponent } from '../home-result/home-result.component';
import { UtilService } from '../util.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [NgOptimizedImage, ReactiveFormsModule,
	    HomeFilterComponent, HomeResultComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  @HostBinding('class.container') container = true
  @ViewChild(HomeResultComponent) result!: HomeResultComponent
  private route = inject(ActivatedRoute)
  private router = inject(Router)
  private util = inject(UtilService)
  private api = inject(ApiService)
  window = window
  ctrl = new FormControl('')
  mobileBarHidden = false
  mobileFilterExpanded = false
  private lastScrollY = 0

  @HostListener('window:scroll')
  onScroll() {
    if (this.window.innerWidth >= 992) return
    if (this.mobileFilterExpanded) return
    const current = this.window.scrollY
    this.mobileBarHidden = current > this.lastScrollY && current > 60
    this.lastScrollY = current
  }

  onMobileFilterExpanded(expanded: boolean) {
    this.mobileFilterExpanded = expanded
    if (expanded) this.mobileBarHidden = false
  }

  ngOnInit() {
    this.ctrl.setValue(this.route.snapshot.queryParams['search'] || '')
    this.ctrl.valueChanges.pipe(debounceTime(300)).subscribe(s => {
      this.router.navigate([], {queryParams: this.util.changedQuery(
	this.route, 'search', s || '')}) })
    /*this.api.getNetworks().subscribe(d => {
      ;(window as any)._allNetworks = d })*/ }
}
