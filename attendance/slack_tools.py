import configparser
import os
import re
from datetime import timedelta, datetime

import slack_sdk


class SlackTools:
    def __init__(self):
        config = configparser.ConfigParser()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(BASE_DIR, 'config.ini')
        config.read(path)

        slack_api_token = config['DEFAULT']['SLACK_API_TOKEN']

        self.slack_client = slack_sdk.WebClient(token=slack_api_token)
        self.channel_id = config['DEFAULT']['CHANNEL_ID']

    def get_slack_client(self):
        return self.slack_client

    def get_channel_id(self):
        return self.channel_id

    def send_no_show_message(self, members):
        message = "[미출석자 알림]\n"
        for member in members:
            message += "@%s " % member

        self.slack_client.chat_postMessage(
            channel='#gardening-for-100days',
            text=message,
            link_names=1
        )

    def get_users(self):
        return self.slack_client.users_list()


    '''
    slack 유저 정보조회
    @:param user: id (e.g. U04L6T16F0D)
    @:return 
    {'ok': True,
     'user':
      {'id': 'U04L6T16F0D',
       'team_id': 'T04LZGEK6RE',
       'name': 'junho85',
       'deleted': False, 'color': '9f69e7',
       'real_name': 'June Kim (김준호)',
       'tz': 'Asia/Seoul', 'tz_label': 'Korea Standard Time', 'tz_offset': 32400,
       'profile': {'title': '출석부관리자', 'phone': '', 'skype': '',
                   'real_name': 'June Kim (김준호)',
                   'real_name_normalized': 'June Kim (김준호)',
                   'display_name': 'June Kim (김준호)',
                   'display_name_normalized': 'June Kim (김준호)', 'fields': None, 'status_text': '', 'status_emoji': '',
                   'status_emoji_display_info': [], 'status_expiration': 0, 'avatar_hash': '873b33c8a4d1',
                   'image_original': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_original.jpg',
                   'is_custom_image': True,
                   'first_name': 'June', 'last_name': 'Kim (김준호)',
                   'image_24': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_24.jpg',
                   'image_32': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_32.jpg',
                   'image_48': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_48.jpg',
                   'image_72': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_72.jpg',
                   'image_192': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_192.jpg',
                   'image_512': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_512.jpg',
                   'image_1024': 'https://avatars.slack-edge.com/2023-01-30/4703448917447_873b33c8a4d1b95cf440_1024.jpg',
                   'status_text_canonical': '', 'team': 'T04LZGEK6RE'},
       'is_admin': True,
       'is_owner': True, 'is_primary_owner': True, 'is_restricted': False, 'is_ultra_restricted': False, 'is_bot': False,
       'is_app_user': False, 'updated': 1675081703, 'is_email_confirmed': True,
       'who_can_share_contact_card': 'EVERYONE'}
    }
    '''
    def get_user(self, user):
        return self.get_slack_client().users_info(
            user=user
        )

    def get_users_id_name_dictionary(self):
        users_list = self.slack_client.users_list()

        return {member['id']: member['name'] for member in users_list["members"]}

    def get_user_names(self):
        return [user["name"] for user in self.get_users()["members"]]

    def get_messages(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        oldest = yesterday.timestamp()
        latest = tomorrow.timestamp()

        response = self.slack_client.conversations_history(
            channel=self.channel_id,
            latest=str(latest),
            oldest=str(oldest),
            count=1000
        )

        return response

    '''
    자기소개채널에서 소개글을 보고 github name리스트 추출
    @:param introduce_channel_id
    @:return github name list
    '''
    def get_github_name_slack_id_dictionary_from_introduce_channel(self, introduce_channel_id):
        p = re.compile('github.com/(\w+)')

        github_name_slack_id_dict = {}

        # 자기소개채널에서 github 주소가 있는 글 추출
        response_conversations_history = self.get_slack_client().conversations_history(
            channel=introduce_channel_id
        )

        for message in response_conversations_history["messages"]:
            if "github.com" in message["text"]:
                # github user name 추출
                github_user_name = p.findall(message["text"])[0]
                github_user_name = github_user_name.split("/")[0]

                # slack user id 정보 조합
                github_name_slack_id_dict[github_user_name] = message["user"]
        return github_name_slack_id_dict

    def get_author_name_from_commit_message(self, message):
        p = re.compile("by (.*)")
        github_id = p.findall(message)[0]
        return github_id

    def test_slack(self):
        # self.slack_client.chat_postMessage(
        #     channel='#junekim', # temp
        #     text='@junho85 test',
        #     link_names=1
        # )
        response = self.slack_client.users_list()
        print(response)
