import { Component, inject } from '@angular/core';
import {NgIf} from '@angular/common'
import {ActivationStart, Router} from '@angular/router'
import {filter, Subscription} from 'rxjs'

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [NgIf],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.css'
})
export class FooterComponent {
  private router = inject(Router)
  private subscription?: Subscription
  window = window

  ngAfterViewInit2() {
    var footer = document.querySelector('footer')
    this.subscription = this.router.events.pipe(filter(e =>
      e instanceof ActivationStart)).subscribe(e => {
	setTimeout(
	  () => {
	    if (!footer) return
	    footer.style.minHeight = `calc(100vh - ${
	      footer.offsetTop}px)` },
	  100) }) }

  ngOnDestroy() { this.subscription?.unsubscribe() }
}
