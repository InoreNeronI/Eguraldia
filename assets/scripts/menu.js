
const hamburger = document.querySelector('.m-h_icon');
document.body.addEventListener('click', e => {
    if (document.body.classList.contains('bg-blur')) {
        return hamburger.dispatchEvent(new Event('click'));
    }
    // @see https://stackoverflow.com/a/153047
    // @see https://css-tricks.com/dangers-stopping-event-propagation
    return e.defaultPrevented;
});
hamburger.addEventListener('click', e => {
    document.body.classList.toggle('bg-blur');
    e.target.parentNode.nextElementSibling.classList.toggle('menu-on');
    const child = e.target.childNodes[1].classList;
    if (child.contains('m-h_icon-to-arrow')) {
        child.remove('m-h_icon-to-arrow');
        child.add('m-h_icon-from-arrow');
        e.target.title = window.texts.MENU_OPEN;
    } else {
        child.remove('m-h_icon-from-arrow');
        child.add('m-h_icon-to-arrow');
        e.target.title = window.texts.MENU_CLOSE;
    }
});
document.querySelector('.m-h_layer').addEventListener('click', e => {
    e.stopPropagation();
    return e.target.parentNode.dispatchEvent(new Event('click'));
});
