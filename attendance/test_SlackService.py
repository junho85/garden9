from datetime import datetime
from unittest import TestCase

from attendance.garden import Garden
from attendance.service.AttendanceService import AttendanceService
from attendance.service.SlackService import SlackService


class TestSlackService(TestCase):

    def setUp(self) -> None:
        self.slack_service = SlackService()
        self.garden = Garden()
        self.attendance_service = AttendanceService()

    def test_send_error_message(self):
        self.slack_service.send_error_message("테스트 에러 메시지")

    def test_send_no_show_message(self):
        today = datetime.today().date()
        # users = self.garden.get_users()
        users = ['junho85']
        self.slack_service.send_no_show_message(attendances=self.attendance_service.get_attendances(
            users=users,
            date=today),
            channel='#test'
        )
