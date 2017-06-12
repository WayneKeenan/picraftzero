from unittest import TestCase

from picraftzero.utils import differential_steering

class SteeringMixerTest(TestCase):

    def test_zero(self):
        (speed_a, speed_b) = differential_steering(0,0)
        self.assertEqual(speed_a, 0, "Speed A not 0")
        self.assertEqual(speed_b, 0, "Speed B not 0")

