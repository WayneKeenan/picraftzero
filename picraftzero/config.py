import logging
import os.path
import json
import ast
from pprint import pformat

logger = logging.getLogger(__name__)

DEFAULT_MONO_URL="ws://${WINDOW_LOCATION_HOSTNAME}:8084/"
#DEFAULT_MONO_URL="http://tiny4wd.local:8080/stream/video.mjpeg"



CONFIG_FILES = [
                "./picraft.cfg",
                "../picraft.cfg",
                "~/.bubbleworks/picraft/conf/picraft.cfg",
                "/home/pi/.bubbleworks/picraft/conf/picraft.cfg",
                "/opt/bubbleworks/picraft/conf/picraft.cfg",
                os.path.join(os.path.split(__file__)[0], "picraft.cfg"),
                ]

config_file = CONFIG_FILES[-1]


DEFAULT_CONFIG = {
    'services_topology': {

        'services': {
            'www':['picraft_www'],
            # 'camera':['uv4l_raspicam'],
        },

        'hosts_services_mapping':{
            #'cam0.local': ['uv4l_raspicam'],
            #'cam1.local': ['uv4l_raspicam'],
            'tiny4wd.local': ['picraft_www'],
        },
    },

    'logging': {
        'debug_enabled': False,
    },

    'inputs': {
        'keyboard_mapping':"8BitDoZero",

    },

    'www': {
        'http_port':8000,
        'ws_port': 8001,
        'ws_protocol': "ws://",
    },

    'hmd': {
        'iconbar_element': 'icon-bar',  # TODO: move to web layer
        #'camera_left_url':  "http://cam0.local:8080/stream/video.mjpeg",
        #'camera_right_url': "http://cam1.local:8080/stream/video.mjpeg",
        #'camera_mono_url':  "http://tiny4wd.local:8080/stream/video.mjpeg",
        #'camera_mono_url':  "ws://${WINDOW_LOCATION_HOSTNAME}:8084/",  # default to the PiStreaming server
        'camera_mono_url': DEFAULT_MONO_URL,
        'camera_view_lx': 13,
        'camera_view_ly': 40,
        'camera_view_rx': 20,
        'camera_view_ry': 60,
    },

    'pantilt': {
        'pan_angle_offset': 0,
        'tilt_angle_offset': 0,
    }
}




def read_config():
    logger.debug("Config file: {}".format(config_file))
    with open(config_file, 'r') as the_file:
        config= ast.literal_eval(the_file.read())
        logger.debug("Read config: {}".format(pformat(config)))
        return config



def write_config(config_dict):
    with open(config_file, 'w') as the_file:
        return the_file.write(pformat(config_dict))



def get_json_config():
    return json.dumps(read_config(), indent=4, sort_keys=True)



def get_config():
    return read_config()


#TODO: disable this after dev
write_config(DEFAULT_CONFIG)
