
import L from 'leaflet';
import 'leaflet-canvasicon';
import 'leaflet-iconmaterial';

const hideOnSuggestEl = document.querySelector('.forecast-arrows');

/**
 * Map class.
 *
 * @constructor
 * @param {String} elId  - The map html id attribute.
 * @param {Number} latEl - The latitude html id attribute.
 * @param {Number} lngEl - The longitude html id attribute.
 */
export class Map {
    constructor(elId, latEl, lngEl, minZoom = 1, maxZoom = 19) {
        // constructor syntactic sugar
        this.elId = elId;
        this.latEl = latEl;
        this.lngEl = lngEl;
        this.latElColor = latEl.parentNode.parentNode.style.color;
        this.lngElColor = lngEl.parentNode.parentNode.style.color;
        this.minZoom = minZoom;
        this.maxZoom = maxZoom;
        this.viewZoom = this.maxZoom / 1.3;
    }

    addMarkerPopup (popup, marker = markers[0]) {
        if (typeof popup !== 'undefined' && popup !== '') {
            marker.bindPopup(popup);
        }
        return popup;
    }

    handleOnBlur() {
        hideOnSuggestEl.style.visibility = 'visible';
    }

    handleOnChange(index) {
        markers.forEach((marker, markerIndex) => {
            if (markerIndex === index) {
                markers = [marker];
                marker.setOpacity(1);
                findBestZoom();
            /*} else {
                removeMarker(marker);*/
            }
        });
    }

    handleOnCursorChanged (e) {
        markers.forEach((marker, markerIndex) => {
            if (markerIndex === e.suggestionIndex) {
                marker.setOpacity(1);
                marker.setZIndexOffset(1);
            } else {
                marker.setZIndexOffset(0);
                marker.setOpacity(0.4);
            }
        });
    }

    handleOnSuggestions (e) {
        hideOnSuggestEl.style.visibility = 'hidden';
        if (e.suggestions.length === 0 || typeof map === 'undefined') {
            return;
        }
        markers.forEach(marker => removeMarker(marker));
        markers = [];

        e.suggestions.forEach(suggestion => addMarker(suggestion));
        findBestZoom();
    }

    /**
     * Remove the map.
     *
     * @return {Boolean}
     */
    off() {
        if (typeof map !== 'undefined') {
            this.latEl.parentNode.parentNode.style.color = this.latElColor;
            this.lngEl.parentNode.parentNode.style.color = this.lngElColor;
            this.latEl.style.color = this.latElColor;
            this.lngEl.style.color = this.lngElColor;
            this.latEl.style.caretColor = this.latElColor;
            this.lngEl.style.caretColor = this.lngElColor;
            this.latEl.style['-webkit-text-fill-color'] = this.latElColor;
            this.lngEl.style['-webkit-text-fill-color'] = this.lngElColor;
            map.remove();
            document.querySelector(`#${this.elId}`).className = '';
            markers.forEach(marker => removeMarker(marker));
            markers = [];
            map = undefined;
            document.querySelector('.forecast').style.display = 'unset';

            return true;
        }
        return false;
    }

    /**
     * Add the map.
     *
     * @param {Number} lat
     * @param {Number} lng
     * @param {Function|undefined} cb
     * @param {*|undefined} cb_arg
     * @return {*}
     */
    on(lat, lng, cb = undefined, cb_arg = undefined) {
        if (typeof map === 'undefined') {
            document.querySelector('.forecast').style.display = 'none';
            this.latEl.parentNode.parentNode.style.color = 'initial';
            this.lngEl.parentNode.parentNode.style.color = 'initial';
            this.latEl.style.color = 'initial';
            this.lngEl.style.color = 'initial';
            this.latEl.style.caretColor = 'initial';
            this.lngEl.style.caretColor = 'initial';
            this.latEl.style['-webkit-text-fill-color'] = 'initial';
            this.lngEl.style['-webkit-text-fill-color'] = 'initial';
            this.latEl.value = lat.toFixed(4);
            this.latEl.dispatchEvent(new Event('change'));
            this.lngEl.value = lng.toFixed(4);
            this.lngEl.dispatchEvent(new Event('change'));
            map = L.map(this.elId, { scrollWheelZoom: true, zoomControl: true });
            map.setView(new L.LatLng(lat, lng), this.viewZoom);
            const tileOSM = new L.TileLayer(
                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: this.maxZoom, minZoom: this.minZoom }
            );
            tileOSM.addTo(map);
        } else {
            map.setView(new L.LatLng(lat, lng), this.viewZoom);
        }
        if (typeof cb === 'function') {
            cb(cb_arg);
        }
        return map;
    }
}

export const addImageMarker = (iconUrl, iconSize, lat, lng, tooltip = null) => {
    const latlng = {latlng: [lat, lng]};
    const suggestion = tooltip ? {...latlng, value: tooltip} : latlng;
    return addMarker(suggestion,{icon: L.icon({iconUrl, iconSize}), opacity: 1, zIndexOffset: 1});
}

export const addMarker = (suggestion, options = {opacity: 0.5, zIndexOffset: 0}) => {
    const htmlEl = document.createElement('div');
    let icon = 'place';
    if (typeof suggestion.hit !== 'undefined') {
        const htmlIconEl = document.createElement('i');
        htmlIconEl.className = 'material-icons';
        htmlIconEl.textContent = suggestion.hit.is_city ? 'location_city' :
            suggestion.hit.is_country ? 'emoji_flags' : suggestion.hit.is_highway ? 'emoji_transportation' :
                suggestion.hit.is_popular ? 'domain' : suggestion.hit.is_suburb ? 'apartment' : icon;
        icon = htmlIconEl.textContent;
        htmlEl.append(htmlIconEl);
    }
    if (typeof suggestion.value !== 'undefined') {
        if (Array.isArray(suggestion.value)) {
            suggestion.value.forEach((value, i) => {
                if (i === 0) {
                    const htmlIconEl = document.createElement('i');
                    htmlIconEl.className = 'material-icons';
                    htmlIconEl.textContent = 'location_city';
                    icon = htmlIconEl.textContent;
                    htmlEl.append(htmlIconEl);
                }
                const htmlTextEl = document.createElement('span');
                htmlTextEl.textContent = value;
                htmlEl.append(htmlTextEl);
            });
        } else {
            const htmlTextEl = document.createElement('span');
            htmlTextEl.textContent = suggestion.value;
            htmlEl.append(htmlTextEl);
        }
    }
    const marker = L.marker(suggestion.latlng, {icon: L.IconMaterial.icon({icon, markerColor: 'inherit'}), ...options});
    if (htmlEl.textContent !== '') {
        marker.bindPopup(htmlEl)/*.openPopup()*/.on('popupopen', e => { // @see https://stackoverflow.com/a/12712987
            if (hasMarkerClass(e.popup._source, 'l-icon-material')) {
                let height = Number(e.popup._source._icon.style.marginTop.replace('px', ''));
                e.popup._container.style.bottom = (e.popup._containerBottom - height).toString() + 'px';
            }
        });
    }
    marker.addTo(map);
    if (hasMarkerClass(marker, 'l-icon-material')) {
        const icon = marker._icon.querySelector('.material-icons');
        icon.setAttribute('x', '3.5');
        icon.setAttribute('y', '25');
    }
    return markers.push(marker);
};

export const addTextMarker = (iconText, iconSize, lat, lng, tooltip = null, heightMultiplier = 1, fontMultiplier = 1) => {
    const icon = L.canvasIcon({
        iconSize,
        //fillStyle: 'rgba(0,0,0,0)',
        drawIcon: function (icon, type) {
            if (type === 'icon') { // type: 'icon' or 'shadow'
                const ctx = icon.getContext('2d');
                const size = L.point([this.options.iconSize[0], this.options.iconSize[1] * heightMultiplier]);
                const center = L.point(Math.floor(size.x / 2), Math.floor(size.y / 2));
                //const radius = Math.min(center.x, center.y);
                ctx.beginPath();
                /*ctx.arc(center.x, center.y, radius, 0, 2 * Math.PI);
                ctx.fillStyle = this.options.fillStyle;
                ctx.fill();*/
                ctx.textAlign = 'center';
                const style = window.getComputedStyle(document.body); // @see https://stackoverflow.com/a/15195404
                const fontSize = Number(style.fontSize.replace('px', '')) * fontMultiplier;
                ctx.font = fontSize.toFixed(6).toString() + 'px ' + style.fontFamily;
                iconText.split('\n').forEach((text, i) => {
                    ctx.fillStyle = i % 2 === 0 ? 'navy' : 'firebrick';
                    ctx.fillText(text, center.x, center.y + fontSize * (i - heightMultiplier));
                });
                ctx.closePath();
            }
        }
    });
    const latlng = {latlng: [lat, lng]};
    const suggestion = tooltip ? {...latlng, value: tooltip} : latlng;
    return addMarker(suggestion,{icon, opacity: 1, zIndexOffset: 1});
}

export const findBestZoom = (bufferRatio = 0.5, animate = false) => {
    const featureGroup = L.featureGroup(markers);
    map.fitBounds(featureGroup.getBounds().pad(bufferRatio), { animate });
};

const hasMarkerClass = (marker, cssClass) => Array.from(marker._icon.classList).includes(cssClass);

const removeMarker = marker => map.removeLayer(marker);

export let markers = [];
let map;
