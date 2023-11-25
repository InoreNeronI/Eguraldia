
import placekit from '@placekit/client-js';
import placekitAutocomplete from '@placekit/autocomplete-js';

import '../menu';

const pk = placekit(window.placekit_api_key, {
    language: window.language,
    maxResults: 11
});

const pka = placekitAutocomplete(window.placekit_api_key, {
    language: window.language,
    maxResults: 11,
    target: '#places'
});

const inputEl = document.querySelector('#places');
const inputClearEl = document.querySelector('.icon-clear');
const inputLocateEl = document.querySelector('.icon-pin');

inputClearEl.textContent = 'clear';
inputLocateEl.textContent = navigator.geolocation ? 'add_location' : 'location_off';
inputClearEl.title = window.texts.MAP_CLEAR;
inputLocateEl.title = window.texts.MAP_LOCATE;

inputLocateEl.addEventListener('click', e => {
    inputLocateEl.setAttribute('disabled', '');
    if (navigator.geolocation) { // check if geolocation is available
        errorEl.className = 'info';
        errorEl.textContent = window.texts.ON;
        navigator.geolocation.getCurrentPosition(async response => {
            await pk.reverse({
                coordinates: `${response.coords.latitude}, ${response.coords.longitude}`
            }).then((res) => {
                inputLocateEl.removeAttribute('disabled');
                inputLocateEl.textContent = 'location_on';
                // @see https://github.com/algolia/places/issues/366#issuecomment-263114762
                pka.setValue(`${res.results[0].name}, ${res.results[0].zipcode[0]}, ${res.results[0].city}, ${res.results[0].administrative}`, true);
                errorEl.className = errorElClass;
                errorEl.textContent = errorElText;
                return shape.on(res.results[0].lat, res.results[0].lng, shape.updateFields, res.results[0]);
            });
        }, error => { // @see https://stackoverflow.com/a/14862073
            errorEl.className = 'error';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorEl.textContent = window.texts.DENIED;
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorEl.textContent = window.texts.UNAVAILABLE;
                    break;
                case error.TIMEOUT:
                    errorEl.textContent = window.texts.TIMEOUT;
                    break;
                case error.UNKNOWN_ERROR:
                    errorEl.textContent = window.texts.UNKNOWN;
                    break;
            }
            inputLocateEl.textContent = 'location_off';
            inputLocateEl.removeAttribute('disabled');
        });
    } else {
        errorEl.className = 'warning';
        errorEl.textContent = window.texts.OFF;
        inputLocateEl.textContent = 'location_off';
    }
});

import '../fields';
import { errorEl, Place } from '../place';

export const shape = new Place(pk);
const errorElClass = errorEl.className;
const errorElText = errorEl.textContent;

inputEl.addEventListener('blur', shape.handleOnBlur);
pka.on('pick', (value, item, index) => {
    shape.handleOnChange(index);
    // @see https://github.com/algolia/places/issues/366#issuecomment-263114762
    pka.setValue(`${item.name}, ${item.zipcode[0]}, ${item.city}, ${item.administrative}`, true);
    console.log(item, value);
    return shape.on(item.lat, item.lng, shape.updateFields, item);
});

inputClearEl.addEventListener('click', e => {
    pka.clear();
    if (shape.off() !== false) {
        shape.emptyFields();
        inputLocateEl.textContent = 'add_location';
    }
});
//$places.on('cursorchanged', shape.handleOnCursorChanged);
//$places.on('suggestions', shape.handleOnSuggestions);
