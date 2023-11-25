
/**
 * Get forecast from https://opendata.euskadi.eus/catalogo/-/prediccion-meteorologica-de-2020
 */

import { $lang, API } from './common';
import { cities, errorEl } from '../place';
import { addImageMarker, addTextMarker, findBestZoom } from '../place/map';
import { shape } from '../pages/place';

const url_cities = 'https://opendata.euskadi.eus/contenidos/prevision_tiempo/met_forecast/opendata/met_forecast.xml';
//const url_counties = 'https://opendata.euskadi.eus/contenidos/prevision_tiempo/met_forecast_zone/opendata/met_forecast_zone.xml';
//const url_tendency = 'https://opendata.euskadi.eus/contenidos/tendencias/met_tendency/opendata/met_tendency.xml';
//const url_forecast = 'https://opendata.euskadi.eus/contenidos/ds_meteorologicos/forecast_ds_2020/opendata/data_forecast_ds_2020.zip';

export const request = cb => API.request(url_cities, async (response, base_url) => {
    // parse XML content string to XML DOM object
    const forecasts = API.xml(response).getElementsByTagName('forecasts')[0];
    // access to XML nodes and get node values
    const api = new API;
    api.cities = [];
    api.map = [];
    Array.from(forecasts.getElementsByTagName('forecast')).forEach(forecast => {
        const id = api.data.push({}) - 1;
        forecast.getAttributeNames().forEach(attribute => (api.data[id][attribute] = forecast.getAttribute(attribute)));
        api.cities[id] = [];
        Array.from(forecast.getElementsByTagName('cityForecastDataList')[0].children).forEach((element, index) => {
            api.cities[id][index] = {};
            element.getAttributeNames().forEach(attribute => {
                const attr = attribute === 'cityCode' ? 'code' : attribute === 'cityName' ? 'name' : attribute;
                api.cities[id][index][attr] = element.getAttribute(attribute);
            });
            Array.from(element.children).forEach(async value => {
                if (value.tagName === 'symbol') {
                    Array.from(value.children).forEach(value => {
                        if (value.tagName === 'descriptions') {
                            api.cities[id][index]['description'] = {};
                            Array.from(value.children).forEach(value => {
                                api.cities[id][index]['description'][value.tagName] = value.textContent;
                            });
                        } else if (value.tagName === 'symbolImage') {
                            api.cities[id][index]['image'] = base_url + value.textContent;
                        }
                    });
                    await API.translateMake(api.cities[id][index]['description'], (obj, src, dest = $lang) =>
                        API.translateFetch(obj[src], src, dest).then(text => { api.cities[id][index]['description'][dest] = text; }));
                } else {
                    api.cities[id][index][value.tagName] = value.textContent;
                }
            });
        });
        api.map[id] = [];
        Array.from(forecast.getElementsByTagName('mapSymbolList')[0].children).forEach((element, index) => {
            api.map[id][index] = {};
            Array.from(element.children).forEach(value => {
                if (value.tagName === 'symbolImage') {
                    api.map[id][index]['image'] = base_url + value.textContent;
                } else {
                    api.map[id][index][value.tagName] = value.textContent;
                }
            });
        });
        api.icons.push({});
        api.icons[id]['image'] = base_url + API.firstChild(forecast, 'imageMap');

        api.texts.push({});
        api.childTexts(Array.from(forecast.getElementsByTagName('description')), id, 'description');
    });
    await api.translateAll().then(() => {
        if (api.days.hasOwnProperty(window.now)) {
            document.title = api.days[window.now]['data']['forecastDateText'];
            document.querySelector('header h1').textContent = document.title;
            document.querySelector('.forecast-arrows span').textContent = document.title;
            const containerEl = document.querySelector('.forecast');
            // First build map
            const htmlEl = document.createElement('div');
            htmlEl.style.height = '436px';
            htmlEl.style.position = 'absolute';
            htmlEl.style.width = '437px';
            const imgEl = document.createElement('img');
            imgEl.setAttribute('height', '436');
            imgEl.setAttribute('src', api.days[window.now]['icons']['image']);
            imgEl.setAttribute('title', api.days[window.now]['data']['forecastDateText']);
            imgEl.setAttribute('width', '437');
            htmlEl.append(imgEl);
            api.days[window.now]['map'].forEach(item => {
                const mapEl = document.createElement('div');
                //mapEl.style.height = (item.height * 453.543364223).toString() + 'px';
                mapEl.style.height = '52px';
                mapEl.style.left = (item.positionX * 453.543364223).toString() + 'px';
                mapEl.style.position = 'absolute';
                mapEl.style.top = (item.positionY * 453.543364223).toString() + 'px';
                //mapEl.style.width = (item.width * 453.543364223).toString() + 'px';
                mapEl.style.width = '52px';
                const imgEl = document.createElement('img');
                imgEl.setAttribute('height', '52');
                imgEl.setAttribute('src', item.image);
                imgEl.setAttribute('width', '52');
                mapEl.append(imgEl);
                htmlEl.append(mapEl);
            });
            containerEl.append(htmlEl);
            // Finally forecast texts
            const cbs = []
            const cbs_run = () => cbs.forEach(cb => typeof cb === 'function' ? cb() : null);
            const descriptions = api.days[window.now]['texts']['description'][$lang].split('. ');
            descriptions.forEach((text, i) => {
                if (text.trim() !== '') {
                    const htmlEl = document.createElement('div');
                    htmlEl.className = 'forecast-detail';
                    htmlEl.style.position = 'absolute';
                    htmlEl.style.visibility = 'hidden';
                    const textEl = document.createElement('span');
                    textEl.textContent = text.lastIndexOf('.') === text.length - 1 ? text : text + '.';
                    htmlEl.append(textEl);
                    containerEl.append(htmlEl);
                    htmlEl.style.top = (436 - htmlEl.offsetHeight).toString() + 'px';
                    cbs.push(() => setTimeout(() => {
                        document.querySelectorAll('.forecast-detail').forEach(el => {
                            el.style.visibility = 'hidden';
                        });
                        htmlEl.style.visibility = 'visible';
                    }, 5000 * i));
                }
            });
            cbs_run();
            setInterval(() => cbs_run(), 5000 * descriptions.length);
        } else {
            errorEl.className = 'warning';
            errorEl.textContent = window.texts.NO_DATA;
        }
    }).then(typeof cb === 'function' ? cb() : null).then((mark_size = [60, 60]) => {
        if (api.days.hasOwnProperty(window.now) && api.days[window.now].hasOwnProperty('cities')) {
            const iconClearEl = document.querySelector('.ap-nostyle-icon-clear');
            const iconPinEl = document.querySelector('.ap-nostyle-icon-pin');
            const inputEl = document.querySelector('.ap-nostyle-input');
            const htmlIconEl = document.createElement('button');
            htmlIconEl.className = 'material-icons ap-nostyle-input-icon';
            htmlIconEl.textContent = 'not_listed_location';
            htmlIconEl.title = window.texts.MAP_CITIES;
            iconClearEl.style.right = '1rem';
            iconPinEl.style.right = '1rem';
            htmlIconEl.addEventListener('click', e => {
                api.days[window.now]['cities'].forEach(city => {
                    if (cities.hasOwnProperty(city.code)) {
                        city = {...city, ...cities[city.code]};
                        /*const map = */shape.on(city.lat, city.lng);
                        const mark_text = '↓' + city['tempMin'] + '°C\n↑' + city['tempMax'] + '°C';
                        const tooltip = [city.name, ...city.description[$lang].split(': ').join(':\n').split('\n')];
                        addImageMarker(city.image, mark_size, city.lat, city.lng, tooltip);
                        addTextMarker(mark_text, mark_size, city.lat, city.lng, tooltip, 3.1, 0.9);
                    }
                });
                findBestZoom();
            });
            iconPinEl.insertAdjacentElement('afterend', htmlIconEl);
            inputEl.style.paddingRight = '2.15rem';
        }
    });
});
