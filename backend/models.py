import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime

from database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(50), default="Meeting")
    date = Column(String(20), nullable=True)
    time = Column(String(20), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True)
    samples_distributed = Column(Text, nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)


    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
