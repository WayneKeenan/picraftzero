(function () {
    'use strict';


    var CameraDisplayMode = {
        NONE: 0,
        TWO_CAM_DUAL: 1,
        ONE_CAM_MONO: 2,
        ONE_CAM_DUAL: 3,
        DEFAULT: 0,
    };


    BubbleworksHMD.HeadLook = 'headlook';
    BubbleworksHMD.Gyro = 'gyro';
    BubbleworksHMD.GyroActive = 'gyro_status';


    // Private
    // constants
    var CAMERA_DISPLAY_MODE_KEY = 'CAMERA_DISPLAY_MODE';
    var GYRO_MS_FREQUENCY = 50;
    var MAX_ANGLE_DELTA = 90;



    var gn = new GyroNorm();

    function BubbleworksHMD(opts) {
        var self = this;

        opts = opts || {};
        self._debug = opts.debug || false;
        self._logger = opts.logger || false;
        self._camera_mono_url = opts.camera_mono_url || "localhost";
        self._camera_right_url = opts.camera_right_url || "localhost";
        self._camera_left_url = opts.camera_left_url || "localhost";


        self._camera_mono_url = self._camera_mono_url.replace('${WINDOW_LOCATION_HOSTNAME}', window.location.hostname);
        // Logic state

        self._last_pan_angle = NaN;
        self._last_tilt_angle = NaN;
        self._last_sent_pan_angle = NaN;
        self._last_sent_tilt_angle = NaN;


        // UI State
        self._use_gyro = false;


        // Display config
        self._cameraVerticalOffsetLeft = opts.camera_view_ly || 0;
        self._cameraVerticalOffsetRight = opts.camera_view_ry || 0;

        self._cameraHorizontalOffsetLeft = opts.camera_view_lx || 0;
        self._cameraHorizontalOffsetRight = opts.camera_view_rx || 0;


    }

    BubbleworksHMD.prototype.start = function () {
        var self = this;
        self.init_gyro();
        self.init_ui();
    }


    // ---------------------------------------------
// Gyro

    BubbleworksHMD.prototype.init_gyro = function (opts) {
        var self = this;
        // TODO: be able to pass the opts in
        var args = {
            frequency: GYRO_MS_FREQUENCY,	// ( How often the object sends the values - milliseconds )
            gravityNormalized: true,		// ( If the garvity related values to be normalized )
            orientationBase: GyroNorm.GAME,	// ( Can be GyroNorm.GAME or GyroNorm.WORLD. gn.GAME returns orientation values with respect to the head direction of the device. gn.WORLD returns the orientation values with respect to the actual north direction of the world. )
            decimalCount: 2,				// ( How many digits after the decimal point will there be in the return values )
            logger: console.log,					// ( Function to be called to log messages from gyronorm.js )
            screenAdjusted: false			// ( If set to true it will return screen adjusted values. )
        };

        gn.init(args).then(function () {
            gn.start( function(sensor_data){self.on_gyro_update(sensor_data);});
        }).catch(function (e) {
            console.log("DeviceOrientation or DeviceMotion is not supported by the browser or device");
        });
    }

    BubbleworksHMD.prototype.deinit_gyro = function () {
        var self = this;
        gn.stopLogging();
    }

    BubbleworksHMD.prototype.on_gyro_update = function (sensor_data) {
        var self = this;
        if (self._use_gyro) {
            self.emit(BubbleworksHMD.Gyro, sensor_data);
            self.update_pan_tilt_angles(Math.round(sensor_data.do.alpha), Math.round(sensor_data.do.gamma));
        } else {
            //console.log("Not using gyro");
        }
    }

    // iOS gyro conversion
    // TODO: refering to the pitch/roll/yaw angles as pan/tilt for headlook is a bit premeature in the pipeline
    BubbleworksHMD.prototype.update_pan_tilt_angles = function (pan_angle, tilt_angle) {
        var self = this;
        pan_angle = Math.floor(pan_angle);
        tilt_angle = Math.floor(tilt_angle);
        // angular adjustment because in Landscape mode.  test on iPhone, android may differ...
        if (tilt_angle >= 0)
            pan_angle -= 180;

        if (tilt_angle < 0)
            tilt_angle = 90 + (90 - Math.abs(tilt_angle));

        // Avoid wild swings at the maximums of angle range
        if (isNaN(self.last_pan_angle))  self.last_pan_angle = pan_angle;
        if (isNaN(self.last_tilt_angle)) self.last_tilt_angle = tilt_angle;

        if (Math.abs(self.last_pan_angle - pan_angle) > MAX_ANGLE_DELTA) {
            pan_angle = self.last_pan_angle;
        } else {
            self.last_pan_angle = pan_angle;
        }

        if (Math.abs(self.last_tilt_angle - tilt_angle) > MAX_ANGLE_DELTA) {
            tilt_angle = self.last_tilt_angle;
        } else {
            self.last_tilt_angle = tilt_angle;
        }

        self.emit_pantilt_angles(pan_angle, tilt_angle);
    }


    BubbleworksHMD.prototype.emit_pantilt_angles = function (pan_angle, tilt_angle) {
        var self = this;


        if ((pan_angle == self.last_sent_pan_angle) && (tilt_angle == self.last_sent_tilt_angle))
            return;
        self.emit(BubbleworksHMD.HeadLook,  tilt_angle, 0, pan_angle); // TODO: yaw
        self.last_sent_pan_angle = pan_angle;
        self.last_sent_tilt_angle = tilt_angle
    }


    // -------------------------------------------------------------------------
    // Display handling

    BubbleworksHMD.prototype.init_ui = function () {
        var self = this;
        // UI Input handlers
        $('#gyroStateButton').click(function () {
            self.gyro_button_pressed();
        });
        $('#dualcam_dualview').click(function () {
            self.set_camera_mode(CameraDisplayMode.TWO_CAM_DUAL)
        });
        $('#singlecam_dualview').click(function () {
            self.set_camera_mode(CameraDisplayMode.ONE_CAM_DUAL)
        });
        $('#singlecam_singleview').click(function () {
            self.set_camera_mode(CameraDisplayMode.ONE_CAM_MONO)
        });
        $('#no_cameras').click(function () {
            self.set_camera_mode(CameraDisplayMode.NONE)
        });
        window.addEventListener('resize', function () {self.on_resize();}, true);
        self.init_camera_images();
        self.resize_camera_images();
        self.update_display();
    }

    BubbleworksHMD.prototype.on_resize = function () {
        var self = this;
        self.resize_camera_images();
    }

    BubbleworksHMD.prototype.update_display = function () {
        var self = this;
        self.toggle_button('gyroStateButton', self._use_gyro);
    }

    BubbleworksHMD.prototype.set_camera_mode = function (camera_mode) {
        var self = this;
        bubbleworks_utils.setCookie(CAMERA_DISPLAY_MODE_KEY, camera_mode);
        // Force a reload as it's doesn't seem possible to reliably stop an MJPEG stream any other way.
        window.location.reload(true);
    }

    BubbleworksHMD.prototype.init_camera_images = function () {
        var self = this;
        var camera_mode = parseInt(bubbleworks_utils.getCookie(CAMERA_DISPLAY_MODE_KEY) || CameraDisplayMode.DEFAULT);
        var camera_view = document.getElementById('camera_view');

        // TODO: undo this assumption that if the mono url is a WS then they all are...
        if ( self._camera_mono_url.toLowerCase().startsWith('ws') ) {
            self.setup_ws_camera_mode(camera_view, camera_mode)
        } else {
            self.setup_mjpg_camera_mode(camera_view, camera_mode)
        }
    }

    BubbleworksHMD.prototype.setup_ws_camera_mode = function (camera_view, camera_mode) {
        var self = this;
        switch (camera_mode) {

            case CameraDisplayMode.ONE_CAM_MONO:
                 self.init_one_cam_single_ws();
                break;
            case CameraDisplayMode.ONE_CAM_DUAL:
                self.init_one_cam_dual_ws();
                break;
            case CameraDisplayMode.TWO_CAM_DUAL:
                break;
            case CameraDisplayMode.NONE:
                break;
            default:
                console.log("Unsupported WS camera_mode: " + camera_mode);
                break;
        }
    }

    BubbleworksHMD.prototype.setup_mjpg_camera_mode = function (camera_view, camera_mode) {
        var self = this;
        switch (camera_mode) {

            case CameraDisplayMode.ONE_CAM_DUAL:
                self.init_one_cam_dual_mjpg();
                break;

            case CameraDisplayMode.ONE_CAM_MONO:
                var img = new Image();
                img.id = "singleImg";
                img.src = self._camera_mono_url;
                img.onload = self.resize_camera_images;
                camera_view.appendChild(img);
                break;

            case CameraDisplayMode.TWO_CAM_DUAL:

                var rightImg = new Image();
                rightImg.id = "rightImg";
                rightImg.src = self._camera_right_url;

                var leftImg = new Image();
                leftImg.id = "leftImg";
                leftImg.src = self._camera_left_url;

                var rightDiv = document.createElement('div');
                rightDiv.className += "right";

                var leftDiv = document.createElement('div');
                leftDiv.className += "left";

                var container = document.createElement('div');
                container.className += "container";

                rightDiv.appendChild(rightImg);
                leftDiv.appendChild(leftImg);
                container.appendChild(rightDiv);
                container.appendChild(leftDiv);
                camera_view.appendChild(container);

                break;

            case CameraDisplayMode.NONE:
                break;
            default:
                console.log("Unsupported MJPG camera_mode: " + camera_mode);
                break;
        }

    }

    BubbleworksHMD.prototype.set_view_offsets = function (lx, ly, rx, ry) {
        var self = this;
        self._cameraVerticalOffsetLeft = ly;
        self._cameraHorizontalOffsetLeft = lx;
        self._cameraVerticalOffsetRight  = ry;
        self._cameraHorizontalOffsetRight = rx;
        self.resize_camera_images()
    }


    BubbleworksHMD.prototype.resize_camera_images = function () {
        var self = this;

        var wid = Math.floor(window.innerWidth / 2);

        var left = document.getElementById("leftImg");
        if (left) {
            left.style.position = "absolute";
            left.style.width = wid + 'px';
            left.style.top = self._cameraVerticalOffsetLeft + 'px';
            left.style.left = self._cameraHorizontalOffsetLeft + 'px';

        }

        var right = document.getElementById("rightImg");
        if (right) {
            right.style.position = "absolute";
            right.style.width = wid + 'px';
            right.style.top = self._cameraVerticalOffsetRight + 'px';
            right.style.left = self._cameraHorizontalOffsetRight + 'px';

        }
        var single = document.getElementById("singleImg");

        if (null == single) {
            single = document.getElementById("singleView"); // change to this generic name for all view to support WS and MJPEG
        }
        if (single) {
            single.style.position = "absolute";
            single.style.height = window.innerHeight + 'px';

            var x_pos = Math.floor((wid - (single.width / 2)));
            single.style.left = x_pos + 'px';

        }


    }


    BubbleworksHMD.prototype.init_one_cam_dual_mjpg = function () {
        var self = this;
        var camera_view = document.getElementById('camera_view');
        var html_canvas = document.createElement("canvas");
        var context = 0;
        var image = new Image();
        var canvas_refresh_timer = 0;
        var width = 1, height = 1;
        var image_width = 0;

        initialize();

        function initialize() {
            html_canvas.id = "camera_view_canvas";
            camera_view.appendChild(html_canvas);


            if (!camera_view) {
                console.log("Camera view div not found");
                return;
            }
            context = html_canvas.getContext('2d');

            window.addEventListener('resize', resize_canvas, false);
            image.src = self._camera_mono_url;

            resize_canvas();
            canvas_refresh_timer = window.setInterval(redraw, 10);

        }

        function redraw() {
            if (!image)
                return;
            context.drawImage(image, 0, 0, image_width, height);
            context.drawImage(image, image_width, 0, image_width, height);
        }


        function resize_canvas() {
            width = window.innerWidth;
            height = window.innerHeight;
            image_width = Math.floor(width / 2);
            html_canvas.width = width;
            html_canvas.height = height;
            context.clearRect(0, 0, width, height);

            redraw();
        }

    };

    BubbleworksHMD.prototype.init_one_cam_dual_ws = function () {
        var self = this;
        var camera_view = document.getElementById('camera_view');
        var html_canvas_left = document.createElement("canvas");
        var html_canvas_right = document.createElement("canvas");
        var client = new WebSocket(self._camera_mono_url);
        var context_left = 0;
        var context_right = 0;
        var canvas_refresh_timer = 0;

        var width = 1, height = 1;

        initialize();

        function initialize() {
            //html_canvas_left.id = "camera_view_canvas";
            camera_view.appendChild(html_canvas_left);
            camera_view.appendChild(html_canvas_right);


            if (!camera_view) {
                console.log("Camera view div not found");
                return;
            }
            context_left = html_canvas_left.getContext('2d');
            context_right = html_canvas_right.getContext('2d');

            window.addEventListener('resize', resize_canvas, false);

            resize_canvas();
            canvas_refresh_timer = window.setInterval(redraw, 10);
            self.player = new jsmpeg(client, {canvas: html_canvas_left});

        }

        function redraw() {
            var destCtx = html_canvas_right.getContext('2d');
            destCtx.drawImage(html_canvas_left, 0, 0);
        }


        function resize_canvas() {
            width = window.innerWidth/2;
            height = window.innerHeight;

            var left_x_pos =   width/8;
            var right_x_pos =  width + width/8;

            html_canvas_left.style.position = "absolute";
            html_canvas_left.style.top = 0  + "px";
            html_canvas_left.style.left = left_x_pos  + "px";
            html_canvas_left.width = width;
            html_canvas_left.height = height;
            context_left.clearRect(0, 0, width, height);

            html_canvas_right.style.position = "absolute";
            html_canvas_right.style.top = 0 + "px";
            html_canvas_right.style.left = right_x_pos + "px";
            html_canvas_right.width = width;
            html_canvas_right.height = height;
            context_right.clearRect(0, 0, width, height);
        }

    };

    BubbleworksHMD.prototype.init_one_cam_single_ws = function () {
        var self = this;
        var camera_view = document.getElementById('camera_view');
        var html_canvas_left = document.createElement("canvas");
        var client = new WebSocket(self._camera_mono_url);
        var context_left = 0;

        var width = 1, height = 1;

        initialize();

        function initialize() {
            camera_view.appendChild(html_canvas_left);
            context_left = html_canvas_left.getContext('2d');

            window.addEventListener('resize', resize_canvas, false);

            resize_canvas();
            self.player = new jsmpeg(client, {canvas: html_canvas_left});

        }

        function resize_canvas() {
            console.log("resize_canvas: " + width + ", " + height);
            width = window.innerWidth/2;
            height = window.innerHeight;

            html_canvas_left.style.position = "absolute";
            html_canvas_left.style.top = 0  + "px";
            html_canvas_left.style.left = Math.floor(width/2) + "px";
            html_canvas_left.width = width ;
            html_canvas_left.height = height;
            context_left.clearRect(0, 0, width, height);

        }

    };

    // UI Utils
    BubbleworksHMD.prototype.toggle_button = function (id, state) {
        var self = this;
        if (state) {
            $('#' + id).removeClass('fa-toggle-off').addClass('fa-toggle-on');
        } else {
            $('#' + id).removeClass('fa-toggle-on').addClass('fa-toggle-off');
        }
    };


    // -------------------------------------------------------------------------
    // UI State handling

    BubbleworksHMD.prototype.gyro_button_pressed = function (event) {
        var self = this;
        self._use_gyro = !self._use_gyro;
        self.emit(BubbleworksHMD.GyroActive, self._use_gyro);
        self.update_display();
    };


    MicroEvent.mixin(BubbleworksHMD);

    window.BubbleworksHMD = BubbleworksHMD;

})();
