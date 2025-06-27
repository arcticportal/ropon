import { Routes } from '@angular/router';

import {HomeComponent} from './home/home.component'
import {NetworksComponent} from './networks/networks.component'
import {PagesComponent} from './pages/pages.component'
import {ContactComponent} from './contact/contact.component'

export const suf = ' | RoPON'

export const routes: Routes = [
  {path: '', component: HomeComponent,
   title: 'Registry of Polar Observing Networks'},
  {path: 'networks/:ropon_id', component: NetworksComponent},
  {path: 'ropon-pages/:slug', component: PagesComponent},
  {path: 'contact', component: ContactComponent,
   title: 'Contact RoPON' + suf},
];
