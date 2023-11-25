
const setClass = (el, active) => {
    const field = el.classList.contains('ap-nostyle-input') ?
        el.parentNode.parentNode.parentNode : el.parentNode.parentNode;
    if (active) {
        field.classList.add('field_control-is-active');
    } else {
        field.classList.remove('field_control-is-active');
    }
    el.value === '' ?
        field.classList.remove('field_control-is-filled') : field.classList.add('field_control-is-filled');
}

document.querySelectorAll(`.field_input[type="date"],
    .field_input[type="datetime-local"],
    .field_input[type="email"],
    .field_input[type="file"],
    .field_input[type="image"],
    .field_input[type="month"],
    .field_input[type="number"],
    .field_input[type="password"],
    .field_input[type="range"],
    .field_input[type="search"],
    .field_input[type="tel"],
    .field_input[type="text"],
    .field_input[type="time"],
    .field_input[type="url"],
    .field_input[type="week"],
    textarea.field_input`).forEach(el => {
    el.addEventListener('blur', event => setClass(event.target, false));
    el.addEventListener('change', event => event.target.dispatchEvent(new Event('blur')));
    el.addEventListener('focus', event => setClass(event.target, true));
    setClass(el, document.activeElement === el);
});
