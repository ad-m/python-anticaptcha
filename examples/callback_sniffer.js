(function () {
    if (!window.grecaptcha) {
        console.log('Avoid wrapping before load grecaptcha');
        return;
    };
    if (window.grecaptcha.wrapped) {
        console.log('Avoid multiple wrapping of grecaptcha');
        return;
    };
    const x = grecaptcha.render;
    grecaptcha.render = function () {
        console.log('grecaptcha arguments', arguments);
        const cb = arguments[1].callback;
        if (arguments[1] && arguments[1].callback) {
            window.recaptchaCallback = window.recaptchaCallback || [];
            window.recaptchaCallback.push(arguments[1].callback);
            console.log('recaptchaCallback', window.recaptchaCallback);
        }
        return x(...arguments);
    };
    grecaptcha.wrapped = true;
})();