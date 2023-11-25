
export const $lang = document.documentElement.lang;

export class API {
    constructor(data = [], icons = [], texts = []) {
        // constructor syntactic sugar
        this.data = data;
        this.days = {};
        this.icons = icons;
        this.texts = texts;
    }

    childTexts(elements, id, tagName) {
        elements.forEach(element => {
            this.texts[id][tagName] = {};
            Array.from(element.children).forEach(text => {
                this.texts[id][tagName][text.tagName] = text.textContent;
            });
        });
    }

    static firstChild(elements, tag, prop = 'textContent') {
        const children = elements.getElementsByTagName(tag);

        return children.length > 0 ? children[0][prop] : '';
    }

    // @see https://stackoverflow.com/a/21798825
    static request(url, cb) {
        const r = new XMLHttpRequest();
        r.onreadystatechange = () => {
            if (r.readyState === 4 && r.status === 200) {
                const pathArray = r.responseURL.split( '/' );
                return cb(r.responseText, pathArray[0] + '//' + pathArray[2]);
            }
        };
        r.onerror = () => console.error('API error.');
        r.open('GET', url, true);
        r.overrideMimeType('text/xml; charset=iso-8859-1');
        r.send();
    }

    static timeExtract(str) {
        return str.substring(str.lastIndexOf('[') + 1, str.lastIndexOf(']'));
    }

    translate(index, key) {
        return API.translateMake(this.texts[index][key], (obj, src, dest = $lang) =>
            API.translateFetch(obj[src], src, dest).then(text => { this.texts[index][key][dest] = text; }));
    }

    translateAll() {
        return this.translateDateAndTime().then(() => this.translateText()).then(() => {
            const sections = Object.keys(this).filter(key => ['data', 'days', 'icons', 'texts'].indexOf(key) === -1);
            this.data.forEach((v, k) => {
                if (v['date'] === window.next) {
                    this.days = {...this.days, ...{next: {data: v, icons: this.icons[k], texts: this.texts[k]}}};
                    sections.forEach(section => (this.days.next[section] = this[section][k]));
                } else if (v['date'] === window.today) {
                    this.days = {...this.days, ...{today: {data: v, icons: this.icons[k], texts: this.texts[k]}}};
                    sections.forEach(section => (this.days.today[section] = this[section][k]));
                } else if (v['date'] === window.tomorrow) {
                    this.days = {...this.days, ...{tomorrow: {data: v, icons: this.icons[k], texts: this.texts[k]}}};
                    sections.forEach(section => (this.days.tomorrow[section] = this[section][k]));
                }
            });
        });
    }

    translateDateAndTime() {
        const promises = [];
        this.data.forEach((v, k) => {
            Object.keys(v).forEach(key => {
                if (v[key] !== '') {
                    if (key.indexOf('Date') >= 0) {
                        promises.push(API.translateFetchDate(v[key], 'es', 'en').then(text => {
                            this.data[k]['date'] = text;
                        }));
                        promises.push(API.translateFetchDate(v[key], 'es', $lang, 'medium').then(text => {
                            this.data[k][key + 'Text'] = text;
                        }));
                        promises.push(API.translateFetchDate(v[key], 'es').then(text => {
                            this.data[k][key] = text;
                        }));
                    } else if (key.indexOf('Time') >= 0) {
                        promises.push(API.translateFetchTime(v[key], 'es').then(text => {
                            this.data[k][key] = text;
                        }));
                    }
                } else {
                    console.error(key + ' is empty.')
                }
            });
        });

        return Promise.all(promises);
    }

    translateText() {
        const promises = [];
        this.data.forEach((v, k) => {
            Object.keys(this.texts[k]).forEach(key => promises.push(this.translate(k, key)));
        });

        return Promise.all(promises);
    }

    static translateFetch(text, src='', dest = $lang) {
        return fetch('/translate?dest=' + dest + '&src=' + src + '&text=' + text)
            .then(response => response.text()).catch(error => console.error(error));
    }

    static translateFetchDate(date, src, dest = $lang, variation = 'short') {
        return fetch('/translate-date?date=' + date + '&src=' + src + '&dest=' + dest + '&variation=' + variation)
            .then(response => response.text()).catch(error => console.error(error));
    }

    static translateFetchTime(time, src, dest = $lang, variation = 'short') {
        return fetch('/translate-time?time=' + time + '&src=' + src + '&dest=' + dest + '&variation=' + variation)
            .then(response => response.text()).catch(error => console.error(error));
    }

    static translateMake(obj, cb) {
        if ($lang === 'en' && !obj.hasOwnProperty('en')) {
            if (obj.hasOwnProperty('es')) { return cb(obj, 'es'); }
            else if (obj.hasOwnProperty('eu')) { return cb(obj, 'eu'); }
            else if (obj.hasOwnProperty('fr')) { return cb(obj, 'fr'); }
        }
        else if ($lang === 'es' && !obj.hasOwnProperty('es')) {
            if (obj.hasOwnProperty('en')) { return cb(obj, 'en', 'es'); }
            else if (obj.hasOwnProperty('eu')) { return cb(obj, 'eu', 'es'); }
            else if (obj.hasOwnProperty('fr')) { return cb(obj, 'fr', 'es'); }
        }
        else if ($lang === 'eu' && !obj.hasOwnProperty('eu')) {
            if (obj.hasOwnProperty('en')) { return cb(obj, 'en', 'eu'); }
            else if (obj.hasOwnProperty('es')) { return cb(obj, 'es', 'eu'); }
            else if (obj.hasOwnProperty('fr')) { return cb(obj, 'fr', 'eu'); }
        }
        else if ($lang === 'fr' && !obj.hasOwnProperty('fr')) {
            if (obj.hasOwnProperty('en')) { return cb(obj, 'en', 'fr'); }
            else if (obj.hasOwnProperty('es')) { return cb(obj, 'es', 'fr'); }
            else if (obj.hasOwnProperty('eu')) { return cb(obj, 'eu', 'fr'); }
        }
    }

    static xml(str) {
        return (new DOMParser()).parseFromString(str, 'text/xml');
    }
}
