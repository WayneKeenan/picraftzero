// bit of a mess...
// ---------------------------------------------
// Browser helpers
function go_fullscreen() {
    if (screenfull.enabled) {
        DEBUG("Requesting Fullscreen");
        screenfull.request();
    } else {
        ERROR("Fullscreen not available");
    }
}

function setCookie(key, value) {
    var expires = new Date();
    expires.setTime(expires.getTime() + (1 * 24 * 60 * 60 * 1000));
    document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
}

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
}

// ---------------------------------------------
// Misc Utils


function map(x, in_min, in_max, out_min, out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

var utils = {
    go_fullscreen: go_fullscreen,
    setCookie: setCookie,
    getCookie: getCookie,
    map: map
}

window.bubbleworks_utils = utils;



(function () {
    'use strict';

    function BubbleworksPiCraft(opts) {
        var self = this;
        opts = opts || {};
        self._start_callback = opts.startup;
    }

     BubbleworksPiCraft.prototype.start= function (start_callback) {
         var self = this;
         $(document).ready(function () {
            $.getJSON("/config.json", self._start_callback);
            //addToHomescreen();
        });
    };

    window.BubbleworksPiCraft = BubbleworksPiCraft;
})();

