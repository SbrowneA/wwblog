"use strict";

//TODO make IIFE
function setDatesToUserTimezone() {
    // gets date elements and sets them on the user's timezone
    let elements = document.querySelectorAll(".convert-to-local-date");
    for (let i = 0; i < elements.length; i++) {
        elements[i].innerText = convertDateToUserTimezone(elements[i].innerText);
    }
}

function convertDateToUserTimezone(dateStr) {
    const month = {
        0: 'January',
        1: 'February',
        2: 'March',
        3: 'April',
        4: 'May',
        5: 'June',
        6: 'July',
        7: 'August',
        8: 'September',
        9: 'October',
        10: 'November',
        11: 'December'
    }
    let date = new Date(dateStr.toString());
    let localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    // alert(`${month[localDate.getMonth()]} ${localDate.getDate()}, ${localDate.getFullYear()}, ${localDate.getHours()}:${localDate.getMinutes()}`)
    let hr = localDate.getHours();
    let min = localDate.getMinutes();
    let ampm = (hr >= 12) ? 'p.m.' : 'a.m.';
    if (hr > 12 && min > 0) {
        hr -= 12;
    }
    hr = (hr === 0) ? 12 : hr;
    min = (min < 10) ? "0" + min : min;
    return `${month[localDate.getMonth()]} ${localDate.getDate()}, ${localDate.getFullYear()}, ${hr}:${min} ${ampm}`;
}

setDatesToUserTimezone();

/**
 * searches the document.cookie object to get the value of the cookie name specified if it exists
 * @param name the name of the cookie to get the value for
 * @returns {null} the value of the cookie name if it exists
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check the cookie string begins with name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


(function initButtons() {
    let navBtns = document.getElementsByClassName('navigation-button');
    for (let btn of navBtns) {
        btn.addEventListener("click", () => {
            console.log("click");
            window.location = btn.value;
        });
    }
})();
