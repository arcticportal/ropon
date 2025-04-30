import { Component, inject, Input, Renderer2, ViewChild,
  ElementRef } from '@angular/core';

import {Feature, Map, View} from 'ol'
import {Polygon} from 'ol/geom'
import {fromLonLat} from 'ol/proj'
import {Coordinate} from 'ol/coordinate'
import {OSM, Vector as VectorSource} from 'ol/source'
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer'

import {Obj} from '../util.service'

type Bound = [Coordinate, Coordinate]

function lonLat(box: Obj, x: string, y: string): Coordinate {
  return fromLonLat([box[x].longitude, box[y].latitude]) }

function boxToPoly(box: Obj): Coordinate[] { return [
  lonLat(box, 'southwest', 'southwest'),
  lonLat(box, 'southwest', 'northeast'),
  lonLat(box, 'northeast', 'northeast'),
  lonLat(box, 'northeast', 'southwest'),
  lonLat(box, 'southwest', 'southwest')] }

function geometries(boxes: Obj[]): Coordinate[][] {
  return boxes.map(b => boxToPoly(b['value'])) }

function globalBounds(geoms: Coordinate[][]): Bound {
  if (!geoms.length || !geoms[0].length) return [[0, 0], [0, 0]]
  var [x, y] = geoms[0][0], [X, Y] = geoms[0][0], z, w
  for (var g of geoms) for ([z, w] of g) {
    if (z < x) x = z
    else if (z > X) X = z
    if (w < y) y = w
    else if (w > Y) Y = w }
  return [[x, y], [X, Y]] }

function centre([[x, y], [X, Y]]: Bound): Coordinate {
  return [(x + X) / 2, (y + Y) / 2] }

function zoom([[x, y], [X, Y]]: Bound): number {
  return 5000000 / (X - x) }

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css'
})
export class MapComponent {
  @Input() boxes: Obj[] = []
  private map?: Map
  private renderer = inject(Renderer2)
  @ViewChild('map') mapEl!: ElementRef

  ngOnChanges(changes: Obj) {
    if (!(changes['boxes'] && changes['boxes'].currentValue)) return
    if (!this.boxes.length) return
    var boxes = geometries(this.boxes)
    if (!boxes.length) return
    var b = globalBounds(boxes)
    if (this.mapEl) {
      var el = this.mapEl.nativeElement
      while (el.firstChild) el.removeChild(el.firstChild) }
    this.map = new Map({
      view: new View({center: centre(b), zoom: zoom(b)}),
      layers: [
	new TileLayer({source: new OSM()}),
	new VectorLayer({
	  style: {
	    'stroke-color': [171, 41, 106, 0.7],
	    'stroke-width': 2,
	    'fill-color': [171, 41, 106, 0.2]},
	  source: new VectorSource({features: boxes.map(
	    (g: Coordinate[]) => new Feature(new Polygon([g])))})})],
      target: 'map'}) }
}
