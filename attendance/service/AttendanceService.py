import logging

from attendance.config_tools import ConfigTools
from attendance.mongo_tools import MongoTools
from attendance.repository.AttendanceRepository import AttendanceRepository
from datetime import date, timedelta, datetime


class AttendanceService:
    def __init__(self):
        # logger 세팅
        # level = logging.DEBUG
        level = logging.INFO
        logging.basicConfig(level=level,
                            format='%(asctime)s [%(process)d] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

        self.attendance_repository = AttendanceRepository()

        self.config_tools = ConfigTools()

        self.users_with_slackname = self.config_tools.get_users()
        self.users = list(self.users_with_slackname.keys())

        self.start_date = self.config_tools.get_start_date()

        self.mongo_tools = MongoTools(
            host=self.config_tools.config['MONGO']['HOST'],
            port=self.config_tools.config['MONGO']['PORT'],
            database=self.config_tools.config['MONGO']['DATABASE'],
            username=self.config_tools.config['MONGO']['USERNAME'],
            password=self.config_tools.config['MONGO']['PASSWORD']
        )

    def get_commits_with_ts_by_user(self, user):
        """
        DB에서 특정 유저의 커밋 메시지를 가져옴. DB에 저장된 데이터는 slack 메시지 형태이고 attachments.text 필드에 커밋 메시지가 있음. 모든 메시지가 커밋 메시지는 아니기 때문에 커밋메시지 외에는 필터링 함

        :param user: user e.g. junho85
        :return: [{ts, ts_for_db, commit_text}] 형태의 리스트 반환
        e.g.
        [{
          'ts': '1691935120.120479',
          'ts_for_db': datetime.datetime(2023, 8, 13, 22, 58, 40, 120000, tzinfo=<DstTzInfo 'Asia/Seoul' KST+9:00:00 STD>),
          'commit_text': '`<https://github.com/junho85/TIL/commit/c00d2e4c23915bad48e8e800881bdaf590fe5d20|c00d2e4c>` - 개발자가 알아야 할 데이터 지향 프로그래밍 with JDK20 읽어보기 - 객체 지향 프로그래밍'
        }]

        commit_text 는 slack 메시지의 attachments.text

        Example usage:
            user = 'junho85'
            commits = get_commits_with_ts_by_user(user=user)
        """
        results = []
        for message in self.attendance_repository.get_messages_by_author_name(author_name=user):
            for attachment in message["attachments"]:
                try:
                    """
                    커밋 내역만 추출
                    * 커밋 메시지 특징
                      * text 필드를 가짐
                      * 커밋이 여러개인 경우 개행으로 구분됨. 개행으로 split해서 커밋 메시지를 추출함
                    * 커밋 메시지가 아닌 경우
                      * Pull request opened
                        * text 필드를 가지고 있으므로 주의
                        * 이 경우 pretext 필드가 있고 "Pull request opened by"로 시작하기 때문에 해당 내역을 제외
                    """
                    if self.is_not_commit_message(attachment):
                        continue

                    for commit_text in attachment["text"].split("\n"):
                        results.append({
                            "ts": message["ts"],
                            "ts_for_db": message["ts_for_db"],
                            "commit_text": commit_text
                        })
                except Exception as err:
                    # logging.info(attachment)
                    # logging.info(message["attachments"])
                    # logging.info(err)
                    continue
        return results

    def is_not_commit_message(self, attachment):
        """
        커밋 메시지가 아닌 경우 True를 반환합니다.
        * pretext 필드가 있고 pretext 필드가 "Pull request opened by"로 시작하는 경우 PR 메시지
        :param attachment:
        :return:
        """
        return "pretext" in attachment and attachment["pretext"].startswith("Pull request opened by")

    def find_attendances_by_user(self, user):
        """
        # 특정 유저의 전체 출석부를 생성함
        # TODO 출석부를 DB에 넣고 마지막 생성된 출석부 이후의 데이터로 추가 출석부 만들도록 하자
        :param user:
        :return:
        """
        result = {}

        start_date = self.start_date

        for commit in self.get_commits_with_ts_by_user(user=user):
            # make attend
            ts_datetime = commit["ts_for_db"]
            attend = {
                "ts": ts_datetime,
                "message": commit["commit_text"]
            }

            # current date and date before day1
            date = ts_datetime.date()
            date_before_day1 = date - timedelta(days=1)
            hour = ts_datetime.hour

            if date_before_day1 >= start_date and hour < 3 and date_before_day1 not in result:
                # check before day1. if exists, before day1 is already done.
                result[date_before_day1] = []
                result[date_before_day1].append(attend)
            else:
                # create date commits array
                if date not in result:
                    result[date] = []

                result[date].append(attend)

        return result

    def get_attendances(self, users, date):
        """
        특정일의 출석 데이터 불러오기
        :param users: list of users
        :param date
        :return: list of attendances
        """
        attend_dict = {}

        # get all users attendance info
        for user in users:
            attends = self.find_attendances_by_user(user)
            attend_dict[user] = attends

        result = {}
        result_attendance = []

        # make users - dates - first_ts
        for user in attend_dict:
            if user not in result:
                result[user] = {}

            result[user][date] = None

            if date in attend_dict[user]:
                result[user][date] = attend_dict[user][date][0]["ts"]

            result_attendance.append({"user": user, "first_ts": result[user][date]})

        return result_attendance
