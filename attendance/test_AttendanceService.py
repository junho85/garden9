import logging
from datetime import datetime
from unittest import TestCase

from attendance.garden import Garden
from attendance.service.AttendanceService import AttendanceService


class TestAttendanceService(TestCase):

    def setUp(self) -> None:
        # logger 세팅
        # level = logging.DEBUG
        level = logging.INFO
        logging.basicConfig(level=level,
                            format='%(asctime)s [%(process)d] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

        self.attendance_service = AttendanceService()
        self.garden = Garden()

    def test_get_attendance(self):
        # users = self.garden.get_users()
        # print(users)
        # users = ['junho85']
        users = ['zieunx']
        date = datetime.today().date()
        attendances = self.attendance_service.get_attendances(users=users, date=date)
        logging.info("=====")
        logging.info(attendances)
        # for attendance in attendances:
        #     logging.info("=====")
        #     logging.info(attendance)

    def test_find_attendances_by_user(self):
        user = 'zieunx'
        # user = 'junho85'
        attendances = self.attendance_service.find_attendances_by_user(user=user)
        # logging.info("=====")
        # logging.info(attendances)
        for date, commits in attendances.items():
            logging.info("=====")
            logging.info(date)
            for commit in commits:
                logging.info(commit)

    def test_get_commits_with_ts_by_user(self):
        # user = 'zieunx'
        user = 'junho85'
        commits = self.attendance_service.get_commits_with_ts_by_user(user=user)
        for commit in commits:
            # logging.info("=====")
            logging.info(commit)