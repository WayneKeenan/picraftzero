(function () {
    'use strict';

    function BubbleworksLogging(opts) {
        var self = this;
        opts = opts || {};
        self._debug_enabled = opts.debug_enabled || false;
        self._send_log = opts.websocket_logging_enabled || false;
        self._websocket = opts.websocket || null;

        window.onerror = function (error, url, line) {
            self.ERROR({acc: 'error', data: 'ERR:' + error + ' URL:' + url + ' L:' + line});
        };
    }

    BubbleworksLogging.prototype.INFO = function (msg) {
        var self = this;
        self._log("INFO", msg);
    };

    BubbleworksLogging.prototype.DEBUG = function (msg) {
        var self = this;
        if (!self._debug_enabled)
            return;
        self._log("DEBUG", msg);
    };

    BubbleworksLogging.prototype.ERROR = function (msg) {
        var self = this;
        self._log("ERROR: ", msg);
    };

    BubbleworksLogging.prototype._log = function (category, msg) {
        console.log(category, msg)
        if (self._send_log && _self._websocket) {
            try {
                self._websocket.send_message("BROWSER_DEBUG", msg);
            } catch (e) {
                console.log("Couldn't send error to websocket endpoint: " + e);
            }
        }
    };

    //BubbleworksLogging.get_logger = function() {
    //    return BubbleworksDefaultLogger;
    //}
    //window.BubbleworksDefaultLogger = BubbleworksLogging();

    window.BubbleworksLogging = BubbleworksLogging;
})();


