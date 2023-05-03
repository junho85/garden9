from attendance.config_tools import ConfigTools
from attendance.mongo_tools import MongoTools
from attendance.repository.AttendanceRepository import AttendanceRepository
from datetime import date, timedelta, datetime


class AttendanceService:
    def __init__(self):
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

    def find_attendances_by_user(self, user):
        """
        # 특정 유저의 전체 출석부를 생성함
        # TODO 출석부를 DB에 넣고 마지막 생성된 출석부 이후의 데이터로 추가 출석부 만들도록 하자
        :param user:
        :return:
        """
        mongo_collection = self.mongo_tools.get_collection()

        result = {}

        start_date = self.start_date
        for message in mongo_collection.find({"author_name": user}).sort("ts", 1):
            # make attend
            commits = []
            for attachment in message["attachments"]:
                try:
                    # commit has text field
                    # there is no text field in pull request, etc...
                    commits.append(attachment["text"])
                except Exception as err:
                    print(message["attachments"])
                    print(err)
                    continue

            # skip - if there is no commits
            if len(commits) == 0:
                continue

            # ts_datetime = datetime.fromtimestamp(float(message["ts"]))
            ts_datetime = message["ts_for_db"]
            ts = message["ts"]
            attend = {
                "ts": ts_datetime,
                "tsts": ts,
                "message": commits
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
