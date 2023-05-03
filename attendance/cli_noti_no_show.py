from datetime import datetime

from attendance.garden import Garden
from attendance.service.AttendanceService import AttendanceService
from attendance.service.SlackService import SlackService

garden = Garden()
slack_service = SlackService()
attendance_service = AttendanceService()
today = datetime.today().date()

slack_service.send_no_show_message(
    attendances=attendance_service.get_attendances(
        users=garden.get_users(), date=today)
)
