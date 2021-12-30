"use strict";

(() => {
    function backToLogin() {
        var url = "/login/";
        window.location.replace(url);
    }

    const backBtn = document.getElementById("backToLoginBtn");
    if (backBtn) {
        backBtn.addEventListener("click", backToLogin);
    }

    (function styleFields() {
        const fields = document.forms['set-password-form'].getElementsByTagName('input');
        for (var i = 0; i < fields.length; i++) {
            fields[i].classList.add('form-control');
        }
    })();

})();

