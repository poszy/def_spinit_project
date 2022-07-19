import wheel
import unittest
class Test_Wheel(unittest.TestCase):

    def test_wheel_spin(self):
        a = wheel.Wheel()
        a.get_spin_result()


if __name__ == '__main__':
    unittest.main()
