from os import getenv, environ
from time import sleep

from unittest import TestCase
from unittest.mock import patch
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import picraftzero
from picraftzero import Joystick, Wheelbase, steering_mixer, logger
from picraftzero import PanTilt, scaled_pair


# ------------------------------------------------------------------------
# Constants

BROWSER_WAIT_SECONDS = 10

LEFT_MOTOR_ID  = 0
RIGHT_MOTOR_ID = 1

PAN_SERVO_ID  = 0
TILT_SERVO_ID = 1

MOTOR_JOYSTICK_ID = 0
PANTILT_JOYSTICK_ID = 1


REST_SPEED = 0
MAX_SPEED  = 100

REST_ANGLE = 90
MIN_ANGLE  = 0
MAX_ANGLE  = 180

# Browser co-ordinates (left is top left), not virtual joypad delta
JOY_AXIS_MIN = -100
JOY_AXIS_MAX = 100

JOY_UP     = JOY_AXIS_MIN
JOY_CENTER = 0
JOY_DOWN   = JOY_AXIS_MAX
JOY_LEFT   = JOY_AXIS_MIN
JOY_RIGHT  = JOY_AXIS_MAX



# ------------------------------------------------------------------------
# Mocks

def fake_set_speed(self, speed):
    motor_id = self._motor_id
    logger.debug("{} = {}".format(motor_id, speed))
    VirtualJoystickTest.fake_set_speed_called_values[motor_id].append(speed)


def fake_set_angle(self, angle):
    servo_id = self._servo_id
    logger.debug("{} = {}".format(servo_id, angle))
    VirtualJoystickTest.fake_set_angle_called_values[servo_id].append(angle)

# ------------------------------------------------------------------------

class OccuranceRecorder(object):

    def __init__(self, allow_repeating_items = True):
        self._items = []
        self._allow_repeats = allow_repeating_items

    def append(self, item):
        if not self._allow_repeats and len(self._items)>0 and self._items[-1] == item:
            return
        self._items.append(item)

    def list(self):
        return self._items.copy()

    def clear(self):
        self._items = []

    def __str__(self):
        return str(self._items)

# ------------------------------------------------------------------------

@patch.object(picraftzero.providers.get_motor_provider(), 'set_speed', fake_set_speed)
@patch.object(picraftzero.providers.get_servo_provider(), 'set_angle', fake_set_angle)
class VirtualJoystickTest(TestCase):

    driver = None
    canvas = None
    joystick0 = None
    joystick1 = None
    motors = None
    pantile = None

    IS_CI_BUILD = getenv("CI", False)

    # ------------------------------------------------------------------------
    # One time setup/teardown

    @staticmethod
    def setUpClass():

        VirtualJoystickTest.joystick0 = Joystick(MOTOR_JOYSTICK_ID)
        VirtualJoystickTest.motors = Wheelbase(left=LEFT_MOTOR_ID, right=RIGHT_MOTOR_ID)
        VirtualJoystickTest.motors.source = steering_mixer(VirtualJoystickTest.joystick0.values)
        #VirtualJoystickTest.motors.source_delay = 0.1

        VirtualJoystickTest.joystick1 = Joystick(PANTILT_JOYSTICK_ID)
        VirtualJoystickTest.pan_tilt = PanTilt(pan=PAN_SERVO_ID, tilt=TILT_SERVO_ID)
        VirtualJoystickTest.pan_tilt.source = scaled_pair(VirtualJoystickTest.joystick1.values,
                                                          MAX_ANGLE, MIN_ANGLE,
                                                          JOY_AXIS_MIN, JOY_AXIS_MAX)
        #VirtualJoystickTest.pan_tilt.source_delay = 0.1

        # Setup Selenium

        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'browser': 'ALL'}

        if VirtualJoystickTest.IS_CI_BUILD:
            username = environ["SAUCE_USERNAME"]
            access_key = environ["SAUCE_ACCESS_KEY"]
            capabilities["tunnel-identifier"] = environ["TRAVIS_JOB_NUMBER"]
            capabilities["build"] = environ["TRAVIS_BUILD_NUMBER"]
            capabilities["tags"] = [environ["TRAVIS_PYTHON_VERSION"], "CI"]
            hub_url = "%s:%s@localhost:4445" % (username, access_key)
            VirtualJoystickTest.driver = webdriver.Remote(desired_capabilities=capabilities,
                                                          command_executor="http://%s/wd/hub" % hub_url)
        else:
            #DRIVER = webdriver.Safari()  # see: http://elementalselenium.com/tips/69-safari
            #DRIVER = webdriver.Chrome()   # see: https://sites.google.com/a/chromium.org/chromedriver/downloads
            VirtualJoystickTest.driver = webdriver.Chrome(desired_capabilities=capabilities)

        VirtualJoystickTest.driver.implicitly_wait(BROWSER_WAIT_SECONDS)
        VirtualJoystickTest.driver.maximize_window()
        VirtualJoystickTest.driver.get("http://localhost:8000/")
        VirtualJoystickTest.canvas = VirtualJoystickTest.driver.find_element_by_id("camera_view")

        VirtualJoystickTest.fake_set_speed_called_values= [OccuranceRecorder(allow_repeating_items=False),
                                                           OccuranceRecorder(allow_repeating_items=False)]

        VirtualJoystickTest.fake_set_angle_called_values= [OccuranceRecorder(allow_repeating_items=False),
                                                           OccuranceRecorder(allow_repeating_items=False)]

    @staticmethod
    def tearDownClass():
        logger.info("Ending")
        VirtualJoystickTest.motors.close()
        VirtualJoystickTest.joystick0.close()
        VirtualJoystickTest.joystick1.close()
        VirtualJoystickTest.driver.quit()

    # ------------------------------------------------------------------------
    # Per test setup

    def setUp(self):
        (w, h) = (VirtualJoystickTest.canvas.size['width'], VirtualJoystickTest.canvas.size['height'])
        self.j0_xc = int(w * 0.75)
        self.j0_yc = int(h * 0.50)
        self.j1_xc = int(w * 0.25)
        self.j1_yc = int(h * 0.50)

        # do some sanity checks:

        self.assertNotEqual(LEFT_MOTOR_ID, RIGHT_MOTOR_ID)
        self.assertNotEqual(MOTOR_JOYSTICK_ID, PANTILT_JOYSTICK_ID)

        self.assertEqual(VirtualJoystickTest.canvas.location['x'], 0)
        self.assertEqual(VirtualJoystickTest.canvas.location['y'], 0)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)
        self.assertGreater(self.j0_xc, 0)
        self.assertGreater(self.j0_yc, 0)
        self.assertGreater(self.j1_xc, 0)
        self.assertGreater(self.j1_yc, 0)


        logger.info("Window size = {}".format(VirtualJoystickTest.driver.get_window_size()))
        logger.info("Canvas x, y, w, h  = {}, {}, {}".format(VirtualJoystickTest.canvas.location, w, h))
        logger.info("j0_xc, j0_yc = {}, {}".format(self.j0_xc, self.j0_yc))
        logger.info("j1_xc, j1_yc = {}, {}".format(self.j1_xc, self.j1_yc))

        VirtualJoystickTest.fake_set_speed_called_values[0].clear()
        VirtualJoystickTest.fake_set_speed_called_values[1].clear()
        VirtualJoystickTest.fake_set_angle_called_values[0].clear()
        VirtualJoystickTest.fake_set_angle_called_values[1].clear()


    def tearDown(self):

        # Show JavaScript console log
        for entry in VirtualJoystickTest.driver.get_log('browser'):
            logger.info("JAVASCRIPT_LOG:" + entry['message'])

    # ------------------------------------------------------------------------
    # Helpers

    def check_speeds(self, motor_id, expected_list):
        self.assertEqual(expected_list,
                         VirtualJoystickTest.fake_set_speed_called_values[motor_id].list(),
                         "Unexpected motor speeds for motor_id={}".format(motor_id))

    def check_angles(self, servo_id, expected_list):
        self.assertEqual(expected_list,
                         VirtualJoystickTest.fake_set_angle_called_values[servo_id].list(),
                         "Unexpected servo angles for servo_id={}".format(servo_id))

    def move_mouse(self, o_x, o_y, x, y):
        # force the return to center (-x, -y), doesn't want to play otherwise
        ActionChains(VirtualJoystickTest.driver) \
            .move_to_element_with_offset(VirtualJoystickTest.canvas, o_x, o_y)\
            .click_and_hold()\
            .move_by_offset(x, y)\
            .perform()

        sleep(0.1)

        ActionChains(VirtualJoystickTest.driver) \
            .move_by_offset(-x, -y)\
            .release()\
            .perform()

        # pause at end of test to give websocket comms a chance before moving on.
        sleep(1)

    def move_joystick(self, joystick_id, delta_x, delta_y):
        if joystick_id == 0:
            self.move_mouse(self.j0_xc, self.j0_yc, delta_x, delta_y)
        elif joystick_id == 1:
            self.move_mouse(self.j1_xc, self.j1_yc, delta_x, delta_y)
        else:
            raise ValueError("Not a valid joystick id {}".format(joystick_id))

        # This wasn't necessary in chromedriver 22
        self.move_mouse(self.j0_xc, self.j0_yc, 0, 0)

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    # The tests...

    # ------------------------------------------------------------------------
    # Motor tests

    def test_joystick0_move_up_max(self):
        self.move_joystick(0, JOY_CENTER, JOY_UP)
        self.check_speeds(LEFT_MOTOR_ID,  [REST_SPEED,  MAX_SPEED, REST_SPEED])
        self.check_speeds(RIGHT_MOTOR_ID, [REST_SPEED,  MAX_SPEED, REST_SPEED])

    def test_joystick0_move_down_max(self):
        self.move_joystick(0, JOY_CENTER, JOY_DOWN)
        self.check_speeds(LEFT_MOTOR_ID,  [REST_SPEED, -MAX_SPEED, REST_SPEED])
        self.check_speeds(RIGHT_MOTOR_ID, [REST_SPEED, -MAX_SPEED, REST_SPEED])

    def test_joystick0_move_left_max(self):
        self.move_joystick(0, JOY_LEFT, JOY_CENTER)
        logger.info(VirtualJoystickTest.fake_set_speed_called_values[0])
        logger.info(VirtualJoystickTest.fake_set_speed_called_values[1])

        self.check_speeds(LEFT_MOTOR_ID,  [REST_SPEED, -MAX_SPEED, REST_SPEED])
        self.check_speeds(RIGHT_MOTOR_ID, [REST_SPEED,  MAX_SPEED, REST_SPEED])

    def test_joystick0_move_right_max(self):
        self.move_joystick(0, JOY_RIGHT, JOY_CENTER)
        self.check_speeds(LEFT_MOTOR_ID,  [REST_SPEED,   MAX_SPEED, REST_SPEED])
        self.check_speeds(RIGHT_MOTOR_ID, [REST_SPEED,  -MAX_SPEED, REST_SPEED])


    # ------------------------------------------------------------------------
    # Servo tests

    def test_joystick1_move_up_max(self):
        self.move_joystick(1, JOY_CENTER, JOY_UP)
        self.check_angles(PAN_SERVO_ID,  [REST_ANGLE])
        self.check_angles(TILT_SERVO_ID, [REST_ANGLE, MIN_ANGLE, REST_ANGLE])

    def test_joystick1_move_down_max(self):
        self.move_joystick(1, JOY_CENTER, JOY_DOWN)
        self.check_angles(PAN_SERVO_ID,  [REST_ANGLE])
        self.check_angles(TILT_SERVO_ID, [REST_ANGLE, MAX_ANGLE, REST_ANGLE])

    def test_joystick1_move_left_max(self):
        self.move_joystick(1, JOY_LEFT, JOY_CENTER)
        self.check_angles(PAN_SERVO_ID,  [REST_ANGLE, MAX_ANGLE, REST_ANGLE])
        self.check_angles(TILT_SERVO_ID, [REST_ANGLE])

    def test_joystick1_move_left_max(self):
        self.move_joystick(1, JOY_LEFT, JOY_CENTER)
        self.check_angles(PAN_SERVO_ID,  [REST_ANGLE, MAX_ANGLE, REST_ANGLE])
        self.check_angles(TILT_SERVO_ID, [REST_ANGLE])
