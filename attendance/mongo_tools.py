import configparser
import os
import pymongo
import pytz
from bson.codec_options import CodecOptions


class MongoTools:
    def __init__(self, host, port, database, username, password):
        self.mongo_host = host
        self.mongo_port = port
        self.mongo_database = database
        self.username = username
        self.password = password

        # mongodb collections
        self.mongo_collection_slack_message = "slack_messages"

    def connect_mongo(self):
        return pymongo.MongoClient(
            "mongodb://%s:%s@%s:%s" % (self.username,
                                       self.password,
                                       self.mongo_host,
                                       self.mongo_port)
        )

    def get_database(self):
        conn = self.connect_mongo()

        return conn.get_database(self.mongo_database)

    def get_collection(self):
        db = self.get_database()

        return db.get_collection(self.mongo_collection_slack_message).with_options(
            codec_options=CodecOptions(
                tz_aware=True,
                tzinfo=pytz.timezone('Asia/Seoul')
            )
        )
