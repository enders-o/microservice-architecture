from sqlalchemy import Column, Integer, String
from base import Base
import datetime

class AddFriend(Base):

    __tablename__ = "add_friend"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    source_user_id = Column(String(250), nullable=False)
    source_number_of_friends = Column(Integer, nullable=False)
    friend_user_id = Column(String(250), nullable=False)
    friend_number_of_friends = Column(Integer, nullable=False)
    date_created = Column(String(100), nullable=False)

    def __init__(self, 
                 trace_id, 
                 source_user_id, source_number_of_friends, 
                 friend_user_id, friend_number_of_friends) -> None:
        self.trace_id = trace_id
        self.source_user_id = source_user_id
        self.source_number_of_friends = source_number_of_friends
        self.friend_user_id = friend_user_id
        self.friend_number_of_friends = friend_number_of_friends
        self.date_created = datetime.datetime.now()



        
