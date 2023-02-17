from collections import defaultdict
from unittest import TestCase

from attendance.slack_tools import SlackTools
from attendance.config_tools import ConfigTools
import re


class TestSlackTools(TestCase):
    config_tools = ConfigTools()
    slack_tools = SlackTools(
        slack_api_token=config_tools.get_slack_api_token(),
        commit_channel_id=config_tools.get_commit_channel_id(),
    )

    introduce_channel_id = "C04LA11FZ34"

    def test_get_users(self):
        print(self.slack_tools.get_users())

    def test_get_user_names(self):
        print(self.slack_tools.get_user_names())

    def test_get_user_slacknames(self):
        print(self.config_tools.get_user_slacknames())

    '''
    slack에 있는 유저들 - users.yaml에 등록된 slack이름을 뺌. 거기다가 봇들 제외
    다 등록 되었으면 결과에 아무 유저가 나오면 안됨
    '''

    def test_user_diff(self):
        users = set(self.slack_tools.get_user_names()) \
                - set(self.config_tools.get_user_slacknames()) \
                - {"slackbot",
                   "garden8",
                   "github"}

        for user in users:
            print(user)

    '''
    users.yaml에 등록된 slack이름 - slack에 있는 유저들
    '''

    def test_user_diff2(self):
        print(set(self.config_tools.get_user_slacknames())
              - set(self.slack_tools.get_user_names())
              )

    def test_regex(self):
        p = re.compile('https://github.com/(\w+)')
        message = "<https://github.com/junho85>"

        print(p.findall(message))

    def test_slack_users(self):
        # list to dictionary
        slack_id_name_dict = self.slack_tools.get_users_id_name_dictionary()
        # print(slack_id_name_dict)
        for (id, name) in slack_id_name_dict.items():
            print(id, name)  # e.g. U04L6T16F0D junho85

    '''
    자기소개 방에 있는 유저들의 github 주소를 기준으로 slack name 구하기
    '''

    def test_get_users(self):
        github_name_slack_id_dict = self.slack_tools.get_github_name_slack_id_dictionary_from_introduce_channel(
            self.introduce_channel_id)
        slack_id_name_dict = self.slack_tools.get_users_id_name_dictionary()

        github_name_slack_dict = {}

        for github_name, slack_id in github_name_slack_id_dict.items():
            github_name_slack_dict[github_name] = {"slack_name": slack_id_name_dict[slack_id]}
        # print("-----")
        # print(github_name_slack_id_dict)
        # print("-----")
        # print(slack_id_name_dict)

        print(github_name_slack_dict)

        for github_name, slack in github_name_slack_dict.items():
            print(f'''{github_name}:
  slack: {slack["slack_name"]}''')

    def test_user(self):
        user_id = "U04L6T16F0D"
        r = self.slack_tools.get_user(user_id)
        print(r)

    '''
    channel list 구하기.
     - 자기소개 channel id: C02MA9HUSV9
     - commit channel id: C02N0D83A3A
    '''

    def test_get_channels(self):
        result = self.slack_tools.get_slack_client().conversations_list()
        print(result)

        for channel in result["channels"]:
            print(channel["id"] + ":" + channel["name"])

    def test_get_commit_messages(self):
        response = self.slack_tools.get_slack_client().conversations_history(
            channel=self.config_tools.get_commit_channel_id(),
            count=10
        )

        for message in response["messages"]:
            print(message)
        # print(response)

    def test_get_commit_messages2(self):
        response = self.slack_tools.get_messages()
        print(response)

    def test_get_author_name_from_commit_message(self):
        github_id = self.slack_tools.get_author_name_from_commit_message(
            "[junho85/TIL] 2 new commits pushed  to _master_ by junho85")
        print(github_id)
