// see: https://github.com/jeromeetienne/virtualjoystick.js


(function () {
    'use strict';

    // Constants
    BubbleworksInputs.EIGHTBITDOZERO_MAPPING = "8BitDoZero";

    BubbleworksInputs.FORWARD_KEY= 'FORWARD_KEY';
    BubbleworksInputs.BACKWARD_KEY= 'BACKWARD_KEY';
    BubbleworksInputs.RIGHT_KEY= 'RIGHT_KEY';
    BubbleworksInputs.LEFT_KEY= 'LEFT_KEY';
    BubbleworksInputs.SELECT_KEY= 'SELECT_KEY';
    BubbleworksInputs.BUTTON_A_KEY= 'BUTTON_A_KEY';
    BubbleworksInputs.BUTTON_B_KEY= 'BUTTON_B_KEY';
    BubbleworksInputs.BUTTON_X_KEY= 'BUTTON_X_KEY';
    BubbleworksInputs.BUTTON_Y_KEY= 'BUTTON_Y_KEY';
    BubbleworksInputs.START_KEY= 'START_KEY';
    BubbleworksInputs.L1_KEY= 'L1_KEY';
    BubbleworksInputs.R1_KEY= 'R1_KEY';


    BubbleworksInputs.JoystickMove = 'joystickMove';
    BubbleworksInputs.JoystickMoveBegin = 'joystickDown';
    BubbleworksInputs.JoystickMoveEnd = 'joystickUp';
    BubbleworksInputs.KeyUp = 'keyUp';
    BubbleworksInputs.KeyDown = 'keyDown';

    function BubbleworksInputs(elem, opts) {
        var self= this;
	    opts = opts			|| {};
        self._debug =  opts.debug || false;
        self._elem  = elem;
        self._keyboard_mapping = {}
        self._keymap = opts.keyboard_mapping || null;
        self._last_x_axis = {};
        self._last_y_axis = {};

    }

    // class methods
    BubbleworksInputs.prototype.start = function() {
        var self = this;
        self._init_gamepad_api();
        self._init_virtual_joystick(this._elem);
        self.set_keyboard_mapping(this._keymap);

        var keydown_func = function(e){self.on_key(e, true);};
        var keyup_func = function(e){self.on_key(e, false);};
        document.addEventListener("keydown", keydown_func, true);
		document.addEventListener("keyup",keyup_func, true);
    };


    // -------------------------------------------------------------------------
    // Keyboard handling

    BubbleworksInputs.prototype.on_key = function(event, is_down) {
        var self = this;
        var key = event.key || event.which;
        event.preventDefault();
        console.log("on_key: " + key + ", " + event.keyCode);

        var mapped_key = key;

        if (key in self._keyboard_mapping)
            mapped_key = self._keyboard_mapping[key];


        self.emit(is_down ? BubbleworksInputs.KeyDown : BubbleworksInputs.KeyUp, mapped_key);
    };


    BubbleworksInputs.prototype.set_keyboard_mapping = function(mapping_name) {
        var self = this;
        // Keyboard map for 8bitdo Zero (http://www.8bitdo.com/zero/index.html)
        // Pair with mobile as keyboard:  Power on by pressing Start + B to put into Bluetooth Keyboard mode and pair with device
        if (mapping_name === BubbleworksInputs.EIGHTBITDOZERO_MAPPING) {
            self._keyboard_mapping = {
                'c': BubbleworksInputs.FORWARD_KEY,
                'd': BubbleworksInputs.BACKWARD_KEY,
                'e': BubbleworksInputs.LEFT_KEY,
                'f': BubbleworksInputs.RIGHT_KEY,
                'n': BubbleworksInputs.SELECT_KEY,
                'g': BubbleworksInputs.BUTTON_A_KEY,
                'j': BubbleworksInputs.BUTTON_B_KEY,
                'h': BubbleworksInputs.BUTTON_X_KEY,
                'i': BubbleworksInputs.BUTTON_Y_KEY,
                'o': BubbleworksInputs.START_KEY,
                'k': BubbleworksInputs.L1_KEY,
                'm': BubbleworksInputs.R1_KEY,

            };
        } else {
            // default key map:
            self._keyboard_mapping = {
                'w': BubbleworksInputs.FORWARD_KEY,
                's': BubbleworksInputs.BACKWARD_KEY,
                'a': BubbleworksInputs.LEFT_KEY,
                'd': BubbleworksInputs.RIGHT_KEY,
                'g': BubbleworksInputs.START_KEY,
                'h': BubbleworksInputs.SELECT_KEY,
                'l': BubbleworksInputs.BUTTON_A_KEY,
                'p': BubbleworksInputs.BUTTON_B_KEY,
                'k': BubbleworksInputs.BUTTON_X_KEY,
                'o': BubbleworksInputs.BUTTON_Y_KEY,
                'q': BubbleworksInputs.L1_KEY,
                'e': BubbleworksInputs.R1_KEY,
            };
        }

    }


    // -------------------------------------------------------------------------
    // HTML5 GamePad handling
    BubbleworksInputs.prototype._init_gamepad_api = function() {
        var self = this;
        // see: http://luser.github.io/gamepadtest/
        var haveEvents = 'GamepadEvent' in window;
        var haveWebkitEvents = 'WebKitGamepadEvent' in window;
        var controllers = {};
        var rAF = window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.requestAnimationFrame;

        function connecthandler(e) {
            addgamepad(e.gamepad);
        }

        function addgamepad(gamepad) {
            controllers[gamepad.index] = gamepad;
            rAF(updateStatus);
        }

        function disconnecthandler(e) {
            removegamepad(e.gamepad);
        }

        function removegamepad(gamepad) {
            delete controllers[gamepad.index];
        }

        function updateStatus() {
            scangamepads();
            var j;
            for (j in controllers) {
                var controller = controllers[j];
                for (var i = 0; i < controller.buttons.length; i++) {
                    var val = controller.buttons[i];
                    var pressed = val == 1.0;
                    if (typeof(val) == "object") {
                        pressed = val.pressed;
                        val = val.value;
                    }
                    var pct = Math.round(val * 100) + "%";
                    if (pressed) {
                        //DEBUG("button pressed:" + pct)
                        //self.emit("buttonPressed", i, val);
                    }
                }

                for (var i = 0; i < controller.axes.length; i++) {
                    //DEBUG(i + ": " + controller.axes[i].toFixed(4));

                }

                var x_axis = Math.floor(controller.axes[2] * 100);
                var y_axis = Math.floor(controller.axes[3] * 100);
                self.emit_joypad_axis(0, x_axis, y_axis);

                x_axis = Math.floor(controller.axes[0] * 100);
                y_axis = Math.floor(controller.axes[1] * 100);
                self.emit_joypad_axis(1, x_axis, y_axis);

            }
            rAF(updateStatus);
        }

        function scangamepads() {
            var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
            for (var i = 0; i < gamepads.length; i++) {
                if (gamepads[i]) {
                    if (!(gamepads[i].index in controllers)) {
                        addgamepad(gamepads[i]);
                    } else {
                        controllers[gamepads[i].index] = gamepads[i];
                    }
                }
            }
        }


        if (haveEvents) {
            window.addEventListener("gamepadconnected", connecthandler);
            window.addEventListener("gamepaddisconnected", disconnecthandler);
        } else if (haveWebkitEvents) {
            window.addEventListener("webkitgamepadconnected", connecthandler);
            window.addEventListener("webkitgamepaddisconnected", disconnecthandler);
        } else {
            setInterval(scangamepads, 500);
        }
    }

    // -------------------------------------------------------------------------
    // Virtual joypad
    BubbleworksInputs.prototype._init_virtual_joystick = function(elem) {
        var self = this;

        var joypad_left_active = false;
        var joypad_right_active = false;
        var active_joystick_id = -1;

        console.log("touchscreen is: " + (VirtualJoystick.touchScreenAvailable() ? "available" : "not available"));

        var virtual_joystick_opts = {
            container: document.getElementById(elem),
            strokeStyle: 'orange',
            stickRadius: 100,
            limitStickTravel: true,
            mouseSupport: true,
        };
        var virtual_joystick = new VirtualJoystick(virtual_joystick_opts);

        var on_virtual_joystick_down = function (event) {
            var x = 0;
            if (event.changedTouches) {
                x = event.changedTouches[0].pageX;
            } else {
                x = event.clientX;
            }
            self.emit(BubbleworksInputs.JoystickMoveBegin, active_joystick_id);

            joypad_left_active = x < (window.innerWidth / 2);
            joypad_right_active = !joypad_left_active;

            if (joypad_left_active)
                active_joystick_id = 1;
            else
                active_joystick_id = 0;

            return true;
        };

        var on_virtual_joystick_up = function (event) {
            self.emit(BubbleworksInputs.JoystickMoveEnd, active_joystick_id);

            // Workaround: Fake a move event
            // self.emit_joypad_axis(active_joystick_id, 0, 0);

            joypad_left_active = false;
            joypad_right_active = false;
            active_joystick_id = -1;
            return true;
        };

        var on_virtual_joystick_move = function (event) {
            var x_axis = Math.floor(virtual_joystick.deltaX());
            var y_axis = Math.floor(virtual_joystick.deltaY());
            self.emit_joypad_axis(active_joystick_id, x_axis, -y_axis);
            return true;
        };

        virtual_joystick.addEventListener('touchStart', on_virtual_joystick_down);
        virtual_joystick.addEventListener('mouseStart', on_virtual_joystick_down);
        virtual_joystick.addEventListener('touchMove', on_virtual_joystick_move);
        virtual_joystick.addEventListener('mouseMove', on_virtual_joystick_move);
        virtual_joystick.addEventListener('touchEnd', on_virtual_joystick_up);

    }


    BubbleworksInputs.prototype.emit_joypad_axis = function(joystick_id, x_axis, y_axis) {
        //console.log("JOYEMIT: " + joystick_id + ", " + x_axis + ", "+  y_axis)
        var self = this;
        x_axis = Math.floor(x_axis);
        y_axis = Math.floor(y_axis);
        if ((x_axis == self._last_x_axis[joystick_id]) && (y_axis == self._last_y_axis[joystick_id]))
            return;
        self.emit(BubbleworksInputs.JoystickMove, joystick_id, x_axis, y_axis);
        self._last_x_axis[joystick_id] = x_axis;
        self._last_y_axis[joystick_id] = y_axis;
    };

    MicroEvent.mixin(BubbleworksInputs);

    window.BubbleworksInputs = BubbleworksInputs;


})();
