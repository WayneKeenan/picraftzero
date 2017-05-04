#!/usr/bin/python3

import logging
import threading

logging.basicConfig(level=logging.INFO , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from time import sleep, time
import pygame

from picraft.utils import arduino_map, default_steering
from picraft.sandpit.input import InputHandler
from picraft.sandpit.hardware import Hardware
from picraft.servers import HTTPServer, WebSocketServer

logger = logging.getLogger(__name__)


class Main:

    def __init__(self):
        self.keep_running = True
        self.x_axis = 0
        self.y_axis = 0
        self.speed_a = 0
        self.speed_b = 0
        self.pan_angle = 90
        self.tilt_angle = 90

        # Dependencies
        self.hw = Hardware()
        self.http_server = HTTPServer()
        self.ws_server = WebSocketServer(self)
        self.input_handler = InputHandler(keyboard_handler=self.on_keyboard_event, joypad_handler=self.on_joypad_event)

    def on_joypad_event(self, event):
        # ABS_RZ =   Rght  YAxis  (top)  0 .. 255 (bottom)
        # ABSZ   =   Right XAxis  (left) 0 .. 255 (right)
        logger.info("{} {}".format(event.code, event.state))

        if event.code == "ABS_Z":
            self.x_axis = event.state - 128
        elif event.code == "ABS_RZ":
            self.y_axis = event.state - 128
        if event.code == "ABS_X":
            self.pan_angle = 180 - arduino_map(event.state, 0, 255, 0, 180)
        elif event.code == "ABS_Y":
            self.tilt_angle = arduino_map(event.state, 0, 255, 0, 180)
        elif event.code == "BTN_TR2" and event.state == 1:
            self.send_all_clients_message('BROWSER_CMD', 'RELOAD_PAGE')




    def on_keyboard_event(self, event):
        if event.type == pygame.KEYDOWN:
            logger.debug(event)
            if event.key == pygame.K_LEFT:
                logger.debug("LEFT")
            if event.key == pygame.K_RIGHT:
                logger.debug("RIGHT")
        if event.type == pygame.KEYUP:
            logger.debug("KEY UP")

    def on_websocket_message(self, message):
        logger.info("on_websocket_message: {}".format(message))
        event_type = message.get('type', None)
        event_data = message.get('data', None)
        event_id = message.get('id', None)

        if event_type == 'JOYSTICK':
            joystick_id = event_id
            (x_axis, y_axis) = event_data

            if joystick_id == 0 and len(event_data) == 3:
                self.x_axis = x_axis
                self.y_axis = y_axis
            elif joystick_id == 1 and len(event_data) == 3:
                self.pan_angle = abs(abs(arduino_map(x_axis, -100, 100, 0, 180)))
                self.tilt_angle = abs(arduino_map(y_axis, -100, 100, 0, 180))
            else:
                logger.error("Unrecognised joystick data {}".format(event_data))

        elif event_type == 'PANTILT':
            (self.pan_angle, self.tilt_angle) = event_data

        else:
            logger.error("Unrecognised event type {}".foramt(event_type))


    def send_all_clients_message(self, type, data):
        message = {'type': type, 'data': data}
        logger.info("Sending webclient message: {}".format(message))
        self.ws_server.send_message(message)


    def _update(self):
        OUTPUT_UPDATE_INTERVAL_MS = 50
        next_update = int(time()*1000) + OUTPUT_UPDATE_INTERVAL_MS

        while self.keep_running:
            if time()*1000 > next_update:
                try:
                    self.hw.set_pan_tilt(self.pan_angle, self.tilt_angle)

                    (self.speed_a, self.speed_b) = default_steering(self.x_axis, self.y_axis)
                    self.hw.set_motor_speeds(-self.speed_a, self.speed_b)
                except Exception as e:
                    logger.exception(e)
                next_update = int(time()*1000) + OUTPUT_UPDATE_INTERVAL_MS
            sleep(0.005)


    def stop(self):
        self.input_handler.stop()
        self.ws_server.stop()
        self.http_server.stop()
        self.hw.stop()

    def start(self):
        self.hw.start()
        self.http_server.start()
        self.ws_server.start()
        self.input_handler.start()

        self.update_thread = threading.Thread(target=self._update, name = __class__)
        self.update_thread.daemon = True
        self.update_thread.start()


        try:
            while self.keep_running:
                logger.debug("poll input...")
                self.input_handler.poll()           # blocking only if device contected!
                # incase input poll doesnt block...
                sleep(1)
                #signal.pause()
        except KeyboardInterrupt:
            pass
        except BaseException as e:
            logger.exception(e)
        finally:
            self.stop()



main = Main()
main.start()
