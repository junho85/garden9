from unittest import TestCase

from attendance.garden import Garden


class TestGarden(TestCase):
    def setUp(self) -> None:
        self.garden = Garden()
