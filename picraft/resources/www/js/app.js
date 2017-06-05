(function (document) {
    'use strict';
    // Libraries
    var picraft, ws, log, hmd, inputs;

    var X_INC = 1;
    var Y_INC = 1;

    var current_view = 1;
    var lx=0, ly=0, rx=0, ry=0;
    var send_joypad_updates = true;
    // ----------------------------------------------------------------------------------------------------
    // Init

    picraft = new BubbleworksPiCraft({'startup': on_startup});
    picraft.start();

    function on_startup(opts) {
        log = new BubbleworksLogging(opts.logging);
        log.DEBUG(opts);

        ws = new BubbleworksWebSocketClient(opts.www);
        ws.on(BubbleworksWebSocketClient.Message, on_message);
        ws.start();

        hmd = new BubbleworksHMD(opts.hmd);
        hmd.on(BubbleworksHMD.HeadLook, on_headlook);
        hmd.on(BubbleworksHMD.GyroActive, on_gyro_state_change);
        hmd.start();


        inputs = new BubbleworksInputs('joystick_view', opts.inputs);
        inputs.on(BubbleworksInputs.JoystickMove, on_joytick_move);
        inputs.on(BubbleworksInputs.JoystickMoveEnd, stop);
        inputs.on(BubbleworksInputs.KeyDown, on_key_down);
        inputs.on(BubbleworksInputs.KeyUp, on_key_up);
        inputs.start();

        ly = opts.hmd.camera_view_ly;
        lx = opts.hmd.camera_view_lx;
        rx = opts.hmd.camera_view_rx;
        ry = opts.hmd.camera_view_ry;
        log.INFO("Started!");
    }


    // ----------------------------------------------------------------------------------------------------
    // Keyboard Handling



    function move_up() {
        //send_joypad_axis(0, 0, 100);
        current_view === 1 ? ly -= Y_INC : ry -= Y_INC;
        hmd.set_view_offsets(lx, ly, rx, ry);
        console.log(lx, ly, rx, ry);
    }
     function move_down() {
        //send_joypad_axis(0, 0, -100);
        current_view === 1 ? ly += Y_INC : ry += Y_INC;
        hmd.set_view_offsets(lx, ly, rx, ry);
        console.log(lx, ly, rx, ry);
    }
   function move_right() {
        //send_joypad_axis(0, 100, 0);
        current_view === 1 ? lx += X_INC : rx += X_INC;
        hmd.set_view_offsets(lx, ly, rx, ry);
        console.log(lx, ly, rx, ry);
    }
    function move_left() {
        //send_joypad_axis(0, -100, 0);
        current_view === 1 ? lx -= X_INC : rx -= X_INC;
        hmd.set_view_offsets(lx, ly, rx, ry);
        console.log(lx, ly, rx, ry);
    }



    var key_handlers = {
        [BubbleworksInputs.FORWARD_KEY]: function () {
            send_joypad_axis(0, 0, 100);
        },
        [BubbleworksInputs.BACKWARD_KEY]: function () {
            send_joypad_axis(0, 0, -100);
        },
        [BubbleworksInputs.RIGHT_KEY]: function () {
            send_joypad_axis(0, 100, 0);
        },
        [BubbleworksInputs.LEFT_KEY]: function () {
            send_joypad_axis(0, -100, 0);
        },
        [BubbleworksInputs.SELECT_KEY]: function () {
            window.location.reload();
        },
        "1": function () {
            current_view = 1;
            log.INFO(current_view);
        },
        "2": function () {
            current_view = 2;
            log.INFO(current_view);
        },

        "ArrowUp": move_up,
        "ArrowDown": move_down,
        "ArrowRight": move_right,
        "ArrowLeft": move_left,
        "UIKeyInputUpArrow": move_up,
        "UIKeyInputDownArrow": move_down,
        "UIKeyInputRightArrow": move_right,
        "UIKeyInputLeftArrow": move_left,
    };

    function on_key_down(key) {
        log.DEBUG("app.on_key_down: " + key);
        if (key in key_handlers) {
            key_handlers[key]();
        }
    }

    function on_key_up(key) {
        log.DEBUG("app.on_key_up: " + key);
        stop();
    }


    // ----------------------------------------------------------------------------------------------------
    //  Joystick Handling

    // Virtual Joystick emits: X Axis (left) -100..100 (bottom)  /   Y Axis (top)  -100..100 (bottom)
    // PanTilt expects:        Pan    (left)  180..000  (right)  /   Tilt   (top)   000..180 (bottom)

    function on_joytick_move(joystick_id, x_axis, y_axis) {
        send_joypad_axis(joystick_id, x_axis, y_axis);
    }

    // ----------------------------------------------------------------------------------------------------
    // HMD handling

    function on_headlook(pitch, roll, yaw) {
        send_pan_tilt_update(yaw, pitch);
    }

    function on_gyro_state_change(state) {
        send_joypad_updates = !state;
    }

    // ----------------------------------------------------------------------------------------------------
    // WebSocket message handling

    function send_joypad_axis(joystick_id, x_axis, y_axis) {
        if (send_joypad_updates) {
            log.DEBUG('Joystick :' + joystick_id + " = (" + x_axis + ", " + y_axis + ")");
            ws.send_message('JOYSTICK', joystick_id, [x_axis, y_axis]);
        }
    }

    function send_pan_tilt_update(pan_angle, tilt_angle) {
        ws.send_message('PANTILT', 0, [pan_angle, tilt_angle]);
    }

    // User Message received from the remote server (e.g. Pi/robot).
    function on_message(type, data) {
    }

    function stop() {
        send_joypad_axis(0, 0, 0);
        send_joypad_axis(1, 0, 0);
    }
})(document);