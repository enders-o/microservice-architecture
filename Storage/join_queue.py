from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class JoinQueue(Base):

    __tablename__ = "join_queue"

    id = Column(Integer, primary_key=True)
    trace_id = Column(String(250), nullable=False)
    user_id = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    game = Column(String(250), nullable=False)
    account_age_days = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, trace_id, user_id, username, game, account_age_days) -> None:
        self.trace_id = trace_id
        self.user_id = user_id 
        self.username = username 
        self.game = game 
        self.account_age_days = account_age_days 
        self.date_created = datetime.datetime.now()
