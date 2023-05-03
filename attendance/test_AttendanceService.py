from datetime import datetime
from unittest import TestCase

from attendance.garden import Garden
from attendance.service.AttendanceService import AttendanceService


class TestAttendanceService(TestCase):

    def setUp(self) -> None:
        self.attendance_service = AttendanceService()
        self.garden = Garden()

    def test_get_attendance(self):
        # users = self.garden.get_users()
        # print(users)
        users = ['junho85']
        date = datetime.today().date()
        attendances = self.attendance_service.get_attendances(users=users, date=date)
        print(attendances)
