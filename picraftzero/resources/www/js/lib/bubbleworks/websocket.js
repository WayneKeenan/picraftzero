(function () {
    'use strict';

    BubbleworksWebSocketClient.Message = 'message';
    BubbleworksWebSocketClient.Opened = 'opened';
    BubbleworksWebSocketClient.Closed = 'closed';

    function BubbleworksWebSocketClient(opts) {
        var self = this;
	    opts = opts			|| {};
        self._debug =  opts.debug|| false;
        self._reconnect_interval = opts.reconnectInterval || 3000;
        self._url = opts.ws_url ||  opts.ws_protocol +  window.location.hostname + ":" + opts.ws_port;
        self._websocket = null;
        self._debug = opts.debug_ || null;

    }

    // class methods
    BubbleworksWebSocketClient.prototype.start = function() {
        var self = this;
        var ws_opts = {debug: this._debug, reconnectInterval: this._reconnect_interval}
        this._websocket = new ReconnectingWebSocket(this._url, null, ws_opts);

        this._websocket.onopen = function (evt) {
            self.emit(BubbleworksWebSocketClient.Opened);
        };

        this._websocket.onclose = function (evt) {
            self.emit(BubbleworksWebSocketClient.Closed);
        };

        this._websocket.onmessage = function (evt) {
            try {
                var msg = JSON.parse(data);
                if (msg.type = 'BROWSER_CMD') {
                    if (msg.data == "RELOAD_PAGE") {
                        window.location.reload(true);
                    }
                }
                self.emit(BubbleworksWebSocketClient.Message, msg.type, msg.data);

            } catch (e) {
                console.log("websocket.onmessage: " + e);
            }
        };
        this._websocket.onerror = function (evt) {
            console.log('ERROR: websocket: ' + evt.data + '\n');
            self._websocket.close();
        };
    };

    BubbleworksWebSocketClient.prototype.send_message = function(type, id, data) {
        if (this.is_connected()) {
            var message = JSON.stringify({'type': type, 'id':id, 'data': data});
            this._websocket.send(message);
        }
    };

    BubbleworksWebSocketClient.prototype.is_connected = function() {
        return this._websocket.readyState ==  WebSocket.OPEN;
    };


    MicroEvent.mixin(BubbleworksWebSocketClient);

    window.BubbleworksWebSocketClient = BubbleworksWebSocketClient;

})();
