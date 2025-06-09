from pymongo import MongoClient
from datetime import datetime


class DB:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["mydatabase"]
        self.chat_history = self.db["history_chat"]


    def add_messages(self,message, session_id, agent_name, type):
        try:
            input_ = {
                "session_id": session_id,
                "agent_name": agent_name,
                "content": message,
                "type": type,
                "created_at": datetime.now()
            }

            insert_reslut = self.chat_history.insert_one(input_)
            print(insert_reslut)
            return "Sucess"
        except Exception as e:
            raise(e)


if __name__=="__main__":
    db  = DB("mongodb://localhost:27017/")
    db.add_messages("test","1","Bedroom","agent_message")