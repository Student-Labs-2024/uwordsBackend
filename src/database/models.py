from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime

from src.database.db_config import Base


class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    subtopics = relationship("SubTopic", back_populates="topic", lazy="selectin")


class SubTopic(Base):
    __tablename__ = "subtopic"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    pictureLink = Column(String, nullable=True)
    topic_title = Column(String, ForeignKey(Topic.title))
    topic = relationship("Topic", back_populates="subtopics", lazy="selectin")


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True, index=True)
    enValue = Column(String)
    ruValue = Column(String)
    audioLink = Column(String, nullable=True)
    pictureLink = Column(String, nullable=True)
    topic = Column(String, ForeignKey(Topic.title))
    subtopic = Column(String, ForeignKey(SubTopic.title))
    userWords = relationship("UserWord", back_populates="word")


class UserWord(Base):
    __tablename__ = "user_word"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey(Word.id))
    user_id = Column(Integer)
    frequency = Column(Integer)
    progress = Column(Integer, default=0)
    latest_study = Column(DateTime)

    word = relationship("Word", back_populates="userWords", lazy="selectin")


class Subscription(Base):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    price = Column(Integer)
    old_price = Column(Integer, nullable=True)
    months = Column(Integer)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    username = Column(String, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    email = Column(String, nullable=True)
    vk_id = Column(String, nullable=True)
    google_id = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    hashed_password = Column(String, nullable=True)
    latest_study = Column(DateTime, nullable=True)
    subscription_acquisition = Column(DateTime, nullable=True)
    subscription_type = Column(ForeignKey(Subscription.id), nullable=True)
    days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)


class Error(Base):
    __tablename__ = "error"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    is_send = Column(Boolean, default=False)
