from datetime import date, timedelta, datetime
from urllib.parse import urlparse

import pymongo
import pprint

import requests

from attendance.service.SlackService import SlackService
from attendance.slack_tools import SlackTools
from attendance.mongo_tools import MongoTools
from attendance.config_tools import ConfigTools


class Garden:
    def __init__(self):
        self.config_tools = ConfigTools()
        self.slack_tools = SlackTools(
            slack_api_token=self.config_tools.get_slack_api_token(),
            commit_channel_id=self.config_tools.get_commit_channel_id(),
        )
        self.mongo_tools = MongoTools(
            host=self.config_tools.config['MONGO']['HOST'],
            port=self.config_tools.config['MONGO']['PORT'],
            database=self.config_tools.config['MONGO']['DATABASE'],
            username=self.config_tools.config['MONGO']['USERNAME'],
            password=self.config_tools.config['MONGO']['PASSWORD']
        )

        self.slack_client = self.slack_tools.get_slack_client()
        self.slack_commit_channel_id = self.slack_tools.get_commit_channel_id()

        self.slack_service = SlackService()

        self.gardening_days = self.config_tools.get_gardening_days()
        self.start_date = self.config_tools.get_start_date()
        self.start_date_str = self.config_tools.get_start_date_str()

        self.users_with_slackname = self.config_tools.get_users()
        self.users = list(self.users_with_slackname.keys())

    def get_gardening_days(self):
        return self.gardening_days

    def get_start_date(self):
        return self.start_date

    def get_start_date_str(self):
        return self.start_date_str

    def get_users(self):
        return self.users

    def find_attend(self, oldest, latest):
        print("find_attend")
        print(oldest)
        print(datetime.fromtimestamp(oldest))
        print(latest)
        print(datetime.fromtimestamp(latest))

        mongo_collection = self.mongo_tools.get_collection()

        for message in mongo_collection.find(
                {"ts_for_db": {"$gte": datetime.fromtimestamp(oldest), "$lt": datetime.fromtimestamp(latest)}}):
            print(message["ts"])
            print(message)

    def collect_slack_messages(self, oldest, latest):
        """
        github 봇으로 모은 slack message 들을 slack_messages collection 에 저장
        :param oldest:
        :param latest:
        :return:
        """
        response = self.slack_client.conversations_history(
            channel=self.slack_commit_channel_id,
            latest=str(latest),
            oldest=str(oldest),
            limit=1000  # default 100
        )

        mongo_collection = self.mongo_tools.get_collection()

        messages = response["messages"]
        for message in messages:
            if "attachments" not in message:
                continue

            # pprint.pprint(message)
            message["ts_for_db"] = datetime.fromtimestamp(float(message["ts"]))
            try:
                message["author_name"] = self.slack_tools.get_author_name_from_commit_message(
                    message["attachments"][0]["fallback"])
            except Exception as err:
                print(message["attachments"])
                print(err)
                continue
            # print(message["author_name"])

            try:
                mongo_collection.insert_one(message)
            except pymongo.errors.DuplicateKeyError as err:
                print(err)
                continue

        return {
            "start": datetime.fromtimestamp(oldest),
            "end": datetime.fromtimestamp(latest),
            "count": len(messages),
        }

    def manual_insert(self, commit_url):
        mongo_collection = self.mongo_tools.get_collection()

        commit = self.get_commit(commit_url)
        # print("commit:")
        # print(commit)
        # print("user:" + commit["user"])
        # print("sha:" + commit["sha"])
        # print("sha_short:" + commit["sha_short"])
        # print("ts:" + commit["ts"])
        # print("ts_datetime:" + str(commit["ts_datetime"]))
        # print("ts_datetime %Y-%m-%d:" + commit["ts_datetime"].strftime("%Y-%m-%d"))
        # print("message:" + commit["message"])

        today = datetime.today().strftime("%Y-%m-%d")
        fallback = '*manual insert %s by june.kim* - commit by %s' % (today, commit["user"])
        text = '`<%s|%s>` - %s' % (commit_url, commit["sha_short"], commit["message"])

        user = 'U05MWPMTQE5'  # github (아무거나 넣어도 상관 없음)
        message = {'attachments':
            [{
                'fallback': fallback,
                'text': text
            }],
            'author_name': commit["user"],
            'ts': commit["ts"],
            'ts_for_db': commit["ts_datetime"],
            'type': 'message',
            'user': user
        }

        pprint.pprint(message)
        # exit(-1)

        try:
            result = mongo_collection.insert_one(message)
            pprint.pprint(result)
            print(message)
            return {"result": "success"}
        except Exception as e:
            print(e)
            return {"result": "fail"}

    def get_commit(self, commit_url):
        parse_result = urlparse(commit_url)
        # print(parse_result)
        (_, user, repo, commit, sha) = parse_result.path.split("/")

        api_url = 'https://api.github.com/repos/%s/%s/commits/%s' % (user, repo, sha)

        r = requests.get(api_url)

        # pprint(r)
        # print(r.json())
        commit_json = r.json()

        ts_datetime = datetime.strptime(commit_json["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%S%z")
        commit_message = commit_json["commit"]["message"]
        ts = str(ts_datetime.timestamp())
        return {
            "user": user,
            "ts": ts,
            "ts_datetime": ts_datetime,
            "sha": sha,
            "sha_short": sha[:8],
            "message": commit_message,
        }
