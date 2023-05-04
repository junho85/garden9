from attendance.config_tools import ConfigTools
from attendance.mongo_tools import MongoTools


class AttendanceRepository:
    def __init__(self):
        self.config_tools = ConfigTools()

        self.mongo_tools = MongoTools(
            host=self.config_tools.config['MONGO']['HOST'],
            port=self.config_tools.config['MONGO']['PORT'],
            database=self.config_tools.config['MONGO']['DATABASE'],
            username=self.config_tools.config['MONGO']['USERNAME'],
            password=self.config_tools.config['MONGO']['PASSWORD']
        )

    def get_messages_by_author_name(self, author_name):
        mongo_collection = self.mongo_tools.get_collection()

        return mongo_collection.find({"author_name": author_name}).sort("ts", 1)