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
        """
        [{ts, ts_for_db, commit_text}] 형태의 리스트를 반환함
        :return:
        """
        # user = 'zieunx'
        user = 'junho85'
        commits = self.attendance_service.get_commits_with_ts_by_user(user=user)
        for commit in commits:
            # logging.info("=====")
            logging.info(commit)
            # 2023-10-18 23:47:01,081 [25291] {test_AttendanceService.py:52} INFO - {'ts': '1691935120.120479', 'ts_for_db': datetime.datetime(2023, 8, 13, 22, 58, 40, 120000, tzinfo=<DstTzInfo 'Asia/Seoul' KST+9:00:00 STD>), 'commit_text': '`<https://github.com/junho85/TIL/commit/c00d2e4c23915bad48e8e800881bdaf590fe5d20|c00d2e4c>` - 개발자가 알아야 할 데이터 지향 프로그래밍 with JDK20 읽어보기 - 객체 지향 프로그래밍'}
