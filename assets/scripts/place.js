
export { Place } from './place/main'; // @see https://stackoverflow.com/a/41058960
import './forecast';

export const cities = {
    2: {lat: 43.2535, lng: -2.93693, name: 'Bilbao'},
    17: {lat: 42.8185, lng: -1.64426, name: 'Iruñea-Pamplona'},
    18: {lat: 43.3224, lng: -1.9839, name: 'Donostia-San Sebastián'},
    19: {lat: 42.8465, lng: -2.6724, name: 'Vitoria-Gasteiz'},
    23: {lat: 43.0657, lng: -2.49008, name: 'Arrasate-Mondragón'},
    24: {lat: 42.5535, lng: -2.58508, name: 'Laguardia'}}

export const errorEl = document.querySelector('.footer .messages span');
