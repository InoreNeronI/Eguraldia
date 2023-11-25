
/**
 * Get sea forecast from https://opendata.euskadi.eus/catalogo/-/prediccion-maritima-2020
 */

import { $lang, API } from './common';
import { errorEl } from '../place';

export const request = cb => API.request('https://opendata.euskadi.eus/contenidos/prevision_maritima/sea_forecast/opendata/sea_forecast.xml', async (response, base_url) => {
    // parse XML content string to XML DOM object
    const forecasts = API.xml(response).getElementsByTagName('forecasts')[0];
    // access to XML nodes and get node values
    const api = new API;
    Array.from(forecasts.getElementsByTagName('forecast')).forEach(forecast => {
        const id = api.data.push({}) - 1;

        forecast.getAttributeNames().forEach(attribute => (api.data[id][attribute] = forecast.getAttribute(attribute)));
        api.data[id]['moonPhaseCode'] = API.firstChild(forecast, 'moonPhaseCode');
        api.data[id]['waterTemperature'] = API.firstChild(forecast, 'waterTemperature');
        api.data[id]['waveHeight'] = API.firstChild(forecast, 'waveHeight');

        api.data[id]['moonRisingTime'] = API.timeExtract(API.firstChild(forecast, 'moonRisingTime'));
        api.data[id]['moonSetTime'] = API.timeExtract(API.firstChild(forecast, 'moonSetTime'));
        api.data[id]['sunRisingTime'] = API.timeExtract(API.firstChild(forecast, 'sunRisingTime'));
        api.data[id]['sunSetTime'] = API.timeExtract(API.firstChild(forecast, 'sunSetTime'));

        api.data[id]['firstHighTide'] = API.firstChild(forecast, 'firstHighTide');
        api.data[id]['secondHighTide'] = API.firstChild(forecast, 'secondHighTide');
        api.data[id]['firstHighTideTime'] = API.timeExtract(API.firstChild(forecast, 'firstHighTideTime'));
        api.data[id]['secondHighTideTime'] = API.timeExtract(API.firstChild(forecast, 'secondHighTideTime'));
        api.data[id]['firstLowTide'] = API.firstChild(forecast, 'firstLowTide');
        api.data[id]['secondLowTide'] = API.firstChild(forecast, 'secondLowTide');
        api.data[id]['firstLowTideTime'] = API.timeExtract(API.firstChild(forecast, 'firstLowTideTime'));
        api.data[id]['secondLowTideTime'] = API.timeExtract(API.firstChild(forecast, 'secondLowTideTime'));

        api.icons.push({});
        api.icons[id]['moonPhase'] = base_url + API.firstChild(forecast, 'moonPhaseIcon');
        api.icons[id]['wave'] = base_url + API.firstChild(forecast, 'waveIcon');
        api.icons[id]['wind'] = base_url + API.firstChild(forecast, 'windIcon');

        api.texts.push({});
        api.texts[id]['synopsis'] = { eu: API.firstChild(forecast, 'synopticalDescription') };
        api.texts[id]['visibility'] = { es: API.firstChild(forecast, 'visibility') };
        api.childTexts(Array.from(forecast.getElementsByTagName('forecastDescription')), id, 'description');
        api.childTexts(Array.from(forecast.getElementsByTagName('moonPhase')), id, 'moonPhase');
    });
    await api.translateAll().then(() => {
        if (api.days.hasOwnProperty(window.now)) {
            const data = api.days[window.now]['data'];
            document.querySelector('.logo').setAttribute('title',
                window.texts.SUN_RISING + ': ' + data['sunRisingTime'] + '\n' +
                window.texts.SUN_SET + ': ' + data['sunSetTime']);
            const htmlEl = document.createElement('span');
            const imgEl = document.createElement('img');
            imgEl.setAttribute('title', data['periodDateText']);
            const iEl = document.createElement('i');
            iEl.className = 'material-icons';
            // Slider
            const sliderItems = document.querySelectorAll('.slider-item');
            // Slider0. Date & Sun times
            sliderItems[0].innerHTML += '&nbsp;';
            // Slider0. Sunrise time
            htmlEl.textContent = data['sunRisingTime'];
            iEl.setAttribute('title', window.texts.SUN_RISING);
            iEl.textContent = 'wb_sunny';
            sliderItems[0].innerHTML += '&nbsp;' + iEl.outerHTML + htmlEl.outerHTML + '&nbsp;';
            // Slider0. Sunset time
            htmlEl.textContent = data['sunSetTime'];
            iEl.setAttribute('title', window.texts.SUN_SET);
            iEl.textContent = 'nights_stay';
            sliderItems[0].innerHTML += '&nbsp;' + iEl.outerHTML + htmlEl.outerHTML + '&nbsp;';
            // Slider1. High tides time
            htmlEl.textContent = data['firstHighTideTime'] + ' (' + data['firstHighTide'] + 'm) | ' +
                data['secondHighTideTime'] + ' (' + data['secondHighTide'] + 'm)';
            iEl.setAttribute('title', window.texts.HIGH_TIDE);
            iEl.textContent = 'waves';
            sliderItems[1].innerHTML = iEl.outerHTML + '&nbsp;' + htmlEl.outerHTML;
            // Slider1. Low tides time
            htmlEl.textContent = data['firstLowTideTime'] + ' (' + data['firstLowTide'] + 'm) | ' +
                data['secondLowTideTime'] + ' (' + data['secondLowTide'] + 'm)';
            iEl.setAttribute('title', window.texts.LOW_TIDE);
            iEl.textContent = 'pool';
            sliderItems[1].innerHTML += '&nbsp;' + iEl.outerHTML + '&nbsp;' + htmlEl.outerHTML;
            // Slider2. Synopsis
            htmlEl.textContent = api.days[window.now]['texts']['synopsis'][$lang];
            sliderItems[2].innerHTML = htmlEl.outerHTML;
            // Slider3. Wind
            imgEl.setAttribute('src', api.days[window.now]['icons']['wind']);
            htmlEl.textContent = api.days[window.now]['texts']['description'][$lang];
            sliderItems[3].innerHTML = imgEl.outerHTML + '&nbsp;' + htmlEl.outerHTML;
            // Slider4. Waves
            imgEl.setAttribute('src', api.days[window.now]['icons']['wave']);
            htmlEl.textContent = window.texts.WAVE_HEIGHT + ': ' + data['waveHeight'] + 'm';
            sliderItems[4].innerHTML = imgEl.outerHTML + '&nbsp;' + htmlEl.outerHTML;
            htmlEl.textContent = '| ' + window.texts.WATER_TEMPERATURE + ': ' + data['waterTemperature'] + '°C';
            sliderItems[4].innerHTML += '&nbsp;' + htmlEl.outerHTML;
            htmlEl.textContent = '| ' + window.texts.VISIBILITY + ': ' + api.days[window.now]['texts']['visibility'][$lang];
            sliderItems[4].innerHTML += '&nbsp;' + htmlEl.outerHTML;
            // Slider5. Moon
            imgEl.setAttribute('src', api.days[window.now]['icons']['moonPhase']);
            htmlEl.textContent = api.days[window.now]['texts']['moonPhase'][$lang];
            sliderItems[5].innerHTML = imgEl.outerHTML + '&nbsp;' + htmlEl.outerHTML;
            htmlEl.textContent = '| ' + window.texts.MOON_RISING + ': ' + data['moonRisingTime'];
            sliderItems[5].innerHTML += '&nbsp;' + htmlEl.outerHTML;
            htmlEl.textContent = '| ' + window.texts.MOON_SET + ': ' + data['moonSetTime'];
            sliderItems[5].innerHTML += '&nbsp;' + htmlEl.outerHTML;
            // Finally start animation, @see https://medium.com/better-programming/how-to-restart-a-css-animation-with-javascript-and-what-is-the-dom-reflow-a86e8b6df00f
            sliderItems.forEach(item => {
                item.classList.add('animate');
                Array.from(item.querySelectorAll('i')).forEach(icon => {
                    htmlEl.className = 'tooltip';
                    htmlEl.textContent = icon.getAttribute('title');
                    htmlEl.style.fontSize = '0.65rem';
                    htmlEl.style.position = 'absolute';
                    htmlEl.style.top = '5%';
                    htmlEl.style.visibility = 'hidden';
                    icon.insertAdjacentHTML('beforeend', htmlEl.outerHTML);
                    setTimeout(() => (icon.querySelector('.tooltip').style.visibility = 'visible'), 3250);
                });
            });
        } else {
            errorEl.className = 'warning';
            errorEl.textContent = window.texts.NO_DATA;
        }
    }).then(typeof cb === 'function' ? cb() : null);
});
