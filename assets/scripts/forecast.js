
import { request as Main } from './forecast/main';
import { request as Sea } from './forecast/sea';

if (window.now === window.today) {
    window.now = 'today';
} else if (window.now === window.tomorrow) {
    window.now = 'tomorrow';
} else if (window.now === window.next) {
    window.now = 'next';
}

Main(Sea);
