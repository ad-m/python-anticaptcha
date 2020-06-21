recaptchaCallback = typeof recaptchaCallback == 'undefined' ? [] : recaptchaCallback;
(function () {
    if (typeof grecaptcha == 'undefined') {
        console.log('Avoid wrapping before load grecaptcha');
        return;
    };
    if (!typeof grecaptcha.recaptchaCallback == 'undefined') {
        console.log('Avoid multiple wrapping of grecaptcha');
        return;
    };
    const x = grecaptcha.render;
    grecaptcha.recaptchaCallback = recaptchaCallback;
    grecaptcha.render = function () {
        console.log('grecaptcha arguments', arguments);
        if (arguments[1] && arguments[1].callback) {
            const cb = arguments[1].callback;
            recaptchaCallback.push(cb);
            console.log('recaptchaCallback', cb);
        }
        return x(...arguments);
    };
})();

funcaptchaCallback = typeof funcaptchaCallback == 'undefined' ? [] : funcaptchaCallback;
(function () {
    if (typeof ArkoseEnforcement == 'undefined'){
        console.log('Avoid wrapping before load ArkoseEnforcement');
        return;
    };
    if (!typeof ArkoseEnforcement.funcaptchaCallback == 'undefined') {
        console.log('Avoid multiple wrapping of ArkoseEnforcement');
        return;
    };
    const extendFuncaptcha = function(cls) {
        function inner() {
            console.log('funcaptcha arguments', arguments);
            if (arguments[0] && arguments[0].callback) {
                const cb = arguments[0].callback;
                recaptchaCallback.push(cb);
                console.log('funcaptchaCallback', cb);
            }
            cls.apply(this, arguments)
        }
        inner.prototype = Object.create(cls.prototype);
        inner.funcaptchaCallback = recaptchaCallback;
        return inner;
    };
    ArkoseEnforcement = new extendFuncaptcha(FunCaptcha);
    FunCaptcha = new extendFuncaptcha(ArkoseEnforcement);
})();