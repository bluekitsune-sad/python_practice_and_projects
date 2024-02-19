import unittest

from pytutorial import the_bigger_one
from pytutorial import the_Trio_Sum


class AllTests(unittest.TestCase):
    def test_bigger_guy(self):
        print('\n\n---------------')
        print('🛠️ Function 👉 bigger_guy()')
        assert the_bigger_one(1, 2) == 2
        assert the_bigger_one(10, 20) == 20
        assert the_bigger_one(20, 10) == 20
        assert the_bigger_one(10, 10) == 10
        print('\nAll Tests Passed (4/4) ✅')
        print('---------------')

    def test_three_sum(self):
        print('\n\n---------------')
        print('🛠️ Function 👉 three_sum()')
        assert the_Trio_Sum(1, 2, 3) == 5
        print('\nAll Tests Passed (4/4) ✅')
        print('---------------')


if __name__ == '__main__':
    unittest.main()
