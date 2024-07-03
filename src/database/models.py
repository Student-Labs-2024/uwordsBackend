from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from src.database.db_config import Base


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True, index=True)
    enValue = Column(String)
    ruValue = Column(String)
    topic = Column(String, nullable=True)
    audioLink = Column(String, nullable=True)
    pictureLink = Column(String, nullable=True)

    userWords = relationship("UserWord", back_populates='word')


class UserWord(Base):
    __tablename__ = "user_word"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey(Word.id))
    user_id = Column(String)
    frequency = Column(Integer)
    progress = Column(Integer, default=0)
    latest_study = Column(DateTime)

    word = relationship("Word", back_populates='userWords', lazy='selectin')


class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)

    subtopics = relationship("SubTopic", back_populates='topic')


class SubTopic(Base):
    __tablename__ = "subtopic"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    topic_id = Column(Integer, ForeignKey(Topic.id))
    
    topic = relationship("Topic", back_populates='subtopics', lazy='selectin')