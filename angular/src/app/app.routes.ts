import { Routes } from '@angular/router';

import {AboutComponent} from './about/about.component'
import {HomeComponent} from './home/home.component'

const suf = ' | RoPON'

export const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'about', component: AboutComponent, title: 'About' + suf}
];
