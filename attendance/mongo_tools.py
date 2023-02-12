import configparser
import os
import pymongo


class MongoTools:
    def __init__(self, host, port, database):
        self.mongo_host = host
        self.mongo_port = port
        self.mongo_database = database

        # mongodb collections
        self.mongo_collection_slack_message = "slack_messages"

    def connect_mongo(self):
        return pymongo.MongoClient("mongodb://%s:%s" % (self.mongo_host, self.mongo_port))

    def get_database(self):
        conn = self.connect_mongo()

        return conn.get_database(self.mongo_database)

    def get_collection(self):
        db = self.get_database()

        return db.get_collection(self.mongo_collection_slack_message)
