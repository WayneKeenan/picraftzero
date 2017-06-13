from unittest import TestCase

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


from picraftzero import Joystick, Wheelbase, steering_mixer, start, stop


class VirtualJoystickTest(TestCase):

    #def setup_module(module):
    #    VirtualJoystickTest.driver = webdriver.Safari()

    #def teardown_module(module):
    #    VirtualJoystickTest.driver.quit()

    def setUp(self):
        self.driver = webdriver.Safari()
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()

        self.joystick = Joystick()
        self.motors   = Wheelbase(left=0, right=1)
        self.motors.source = steering_mixer(self.joystick.values)
        self.driver.get("http://localhost:8000/")


    def tearDown(self):
        self.driver.quit()
        self.motors.close()
        self.joystick.close()

    def test_press_joystick_0(self):
        canvas = self.driver.find_element_by_id("camera_view")

        drawing = ActionChains(self.driver) \
            .click_and_hold(canvas) \
            .move_by_offset(100,100) \
            .move_by_offset(50, 50) \
            .release()


        drawing.perform()


