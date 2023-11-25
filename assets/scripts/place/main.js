
import { addMarker, Map, findBestZoom, markers } from './map';
import { $lang } from '../forecast/common';

const latEl = document.querySelector('#reverse-geo-lat');
const lngEl = document.querySelector('#reverse-geo-lng');
const addressEl = document.querySelector('#reverse-address');
const townEl = document.querySelector('#reverse-town');
const regionEl = document.querySelector('#reverse-region');

/**
 * Shape class, @see https://gist.github.com/remarkablemark/fa62af0a2c57f5ef54226cae2258b38d
 *
 * @constructor
 * @param {PKClient} places - The places instance.
 * @param {String} map_id - The map html id attribute.
 */
export class Place extends Map {
    constructor(places, map_id = 'map') {
        super(map_id, latEl, lngEl); // call Map's constructor via super
        this.places = places;
        console.log(places);
        this.setLocationEvents();
    }

    /**
     * @see https://stackoverflow.com/a/29773435
     *
     * @param {Number} value
     * @param {Number} maximumFractionDigits
     *
     * @return {String}
     */
    getLocalizedNumber(value, maximumFractionDigits = 4) {
        const sign = Math.sign(value);
        const localized_abs = Math.abs(value).toLocaleString($lang, { maximumFractionDigits });
        return sign === 1 ? localized_abs.toString() : `-${localized_abs.toString()}`;
    }

    /**
     * Get coordinates.
     *
     * @return {*}
     */
    getLocation() {
        return { lat: this.lat, lng: this.lng };
    }

    /**
     * Get around location.
     * @see https://stackoverflow.com/a/56173964
     *
     * @return {Promise<void>}
     */
    getLocationAround() {
        return this.places.reverse(`${this.lat},${this.lng}`, { hitsPerPage: 1, language: $lang });
    }

    /**
     * Around location callback.
     *
     * @param {Object} coords - The `{ lat, lng }` object.
     *
     * @return {Promise<void>}
     */
    locatedAround(coords) {
        this.setLocation(coords.latitude, coords.longitude);
        latEl.value = this.getLocalizedNumber(this.lat);
        latEl.dispatchEvent(new Event('blur'));
        lngEl.value = this.getLocalizedNumber(this.lng);
        lngEl.dispatchEvent(new Event('blur'));
        return this.updateShape();
    }

    /**
     * Set coordinates.
     *
     * @param {Number} lat - The latitude.
     * @param {Number} lng - The longitude.
     */
    setLocation(lat, lng) {
        this.lat = lat.toFixed(6);
        this.lng = lng.toFixed(6);
    }

    /**
     * Set location change callback.
     */
    setLocationEvents() {
        latEl.addEventListener('change', async e => {
            this.lat = parseFloat(e.target.value.replace(',','.')).toFixed(6);
            this.lat === 'NaN' ? this.lat = undefined : await this.updateShape();
        });
        lngEl.addEventListener('change', async e => {
            this.lng = parseFloat(e.target.value.replace(',','.')).toFixed(6);
            this.lng === 'NaN' ? this.lng = undefined : await this.updateShape();
        });
    }

    /**
     * Empty the form and hide some fields.
     */
    emptyFields() {
        latEl.value = '';
        latEl.dispatchEvent(new Event('blur'));
        lngEl.value = '';
        lngEl.dispatchEvent(new Event('blur'));
        addressEl.parentNode.parentNode.style.display = 'none';
        addressEl.value = '';
        addressEl.dispatchEvent(new Event('blur'));
        townEl.parentNode.parentNode.style.display = 'none';
        townEl.value = '';
        townEl.dispatchEvent(new Event('blur'));
        regionEl.parentNode.parentNode.style.display = 'none';
        regionEl.value = '';
        regionEl.dispatchEvent(new Event('blur'));
    }

    /**
     * Update the form.
     *
     * @param {*} r - The response object
     */
    updateFields(r) {
        if (r.latlng) {
            if (markers.length === 0) {
                addMarker(r, {opacity: 1, zIndexOffset: 1});
                findBestZoom();
            }
            latEl.value = r.latlng.lat;
            latEl.dispatchEvent(new Event('blur'));
            lngEl.value = r.latlng.lng
            lngEl.dispatchEvent(new Event('blur'));
        }
        if (r.hit && r.hit.locale_names) {
            const name = r.hit.locale_names.length === 0 ? null : r.hit.locale_names[0];
            const postcode = typeof r.postcode === 'undefined' ? null : r.postcode;
            addressEl.value = name && postcode ? `${name}, ${postcode}` : name ? name : postcode ? postcode : '';
            addressEl.dispatchEvent(new Event('blur'));
            addressEl.parentNode.parentNode.style.display = addressEl.value === '' ? 'none' : 'inherit';
            const suburb = typeof r.suburb === 'undefined' ? null : r.suburb;
            const city = typeof r.city === 'undefined' ? null : r.city;
            townEl.value = suburb && city ? `${suburb}, ${city}` : suburb ? suburb : city ? city : '';
            townEl.dispatchEvent(new Event('blur'));
            townEl.parentNode.parentNode.style.display = townEl.value === '' ? 'none' : 'inherit';
            let county = typeof r.county === 'undefined' ? null : r.county;
            const region = typeof r.administrative === 'undefined' ? null : r.administrative;
            county = county === region ? null : county;
            const country = typeof r.country === 'undefined' ? null : r.country;
            const rest = region && country ? `${region}, ${country}` : region ? region : country ? country : null;
            regionEl.value = county && rest ? `${county}, ${rest}` : county ? county : rest ? rest : '';
            regionEl.dispatchEvent(new Event('blur'));
            regionEl.parentNode.parentNode.style.display = regionEl.value === '' ? 'none' : 'inherit';
        }
    }

    /**
     * Update the form and the map.
     *
     * @return {Promise<*>}
     */
    updateShape() {
        if (typeof this.lat !== 'undefined' && typeof this.lng !== 'undefined') {
            return this.getLocationAround().then(r => {
                if (this.off() !== false) {
                    this.emptyFields();
                }
                this.on(this.lat, this.lng, this.updateFields, r[0]);
                return this.addMarkerPopup(r[0].value);
            });
        }
    }
}
