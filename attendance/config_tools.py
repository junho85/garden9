import configparser
import os
from datetime import date, timedelta, datetime
import yaml


class ConfigTools:
    def __init__(self):
        self.config_dir = self.init_config_dir()
        self.config = self.load_config()
        self.users = self.load_users()

    def init_config_dir(self):
        env_config_dir = os.environ.get('GARDEN_CONFIG_DIR')
        if env_config_dir:
            return env_config_dir

        config_dir = "/config/attendance"
        return config_dir

    def load_config(self):
        config = configparser.ConfigParser()
        path = os.path.join(self.config_dir, 'config.ini')
        config.read(path)
        return config

    def get_config(self):
        return self.config

    def get_gardening_days(self):
        return self.config['DEFAULT']['GARDENING_DAYS']

    def get_start_date_str(self):
        return self.config['DEFAULT']['START_DATE']

    def get_start_date(self):
        return datetime.strptime(self.get_start_date_str(),
                          "%Y-%m-%d").date()  # start_date e.g.) 2021-01-18

    def load_users(self):
        """
        load users.yaml
        :return: users_with_slackname
        """
        path = os.path.join(self.config_dir, 'users.yaml')
        with open(path) as file:
            users_with_slackname = yaml.full_load(file)

        return users_with_slackname

    def get_users(self):
        return self.users

    def get_user_slacknames(self):
        return [self.users[user]["slack"] for user in self.users]

    def get_monitor_channel_id(self):
        return self.config['MONITOR']['CHANNEL_ID']