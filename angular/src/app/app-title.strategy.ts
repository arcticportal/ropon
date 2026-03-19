import { Injectable } from '@angular/core'
import { Title } from '@angular/platform-browser'
import { ActivatedRouteSnapshot, RouterStateSnapshot, TitleStrategy } from '@angular/router'

import { suf } from './app.routes'

@Injectable({providedIn: 'root'})
export class AppTitleStrategy extends TitleStrategy {
  constructor(private readonly title: Title) { super() }

  override updateTitle(snapshot: RouterStateSnapshot) {
    let route: ActivatedRouteSnapshot = snapshot.root
    while (route.firstChild) route = route.firstChild

    const network = route.data['network']
    const page = route.data['page']

    if (network?.name) {
      this.title.setTitle(network.name + suf)
    } else if (page) {
      const items = page.items
      this.title.setTitle(items?.length ? items[0].title + suf : '404' + suf)
    } else {
      const title = this.buildTitle(snapshot)
      if (title) this.title.setTitle(title)
    }
  }
}
