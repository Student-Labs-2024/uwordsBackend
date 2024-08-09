from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey, DateTime

from src.config.instance import (
    ALLOWED_AUDIO_SECONDS,
    ALLOWED_VIDEO_SECONDS,
    DEFAULT_ENERGY,
)
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
    latest_update = Column(DateTime, nullable=True)
    subscription_acquisition = Column(DateTime, nullable=True)
    subscription_type = Column(ForeignKey(Subscription.id), nullable=True)
    days = Column(Integer, default=0)
    allowed_audio_seconds = Column(Integer, default=ALLOWED_AUDIO_SECONDS)
    allowed_video_seconds = Column(Integer, default=ALLOWED_VIDEO_SECONDS)
    energy = Column(Integer, default=DEFAULT_ENERGY)
    created_at = Column(DateTime, default=datetime.now)

    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    user_achievements = relationship(
        "UserAchievement", back_populates="user", lazy="selectin"
    )


class Error(Base):
    __tablename__ = "error"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    is_send = Column(Boolean, default=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    stars = Column(Integer, nullable=False)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class Bill(Base):
    __tablename__ = "bill"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)
    sub_type = Column(ForeignKey(Subscription.id))
    amount = Column(Integer)
    success = Column(Boolean, default=False)


class Achievement(Base):
    __tablename__ = "achievement"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    pictureLink = Column(String, nullable=True)
    category = Column(String)
    stage = Column(Integer)
    target = Column(Integer, nullable=False)
    user_achievements = relationship(
        "UserAchievement", back_populates="achievement", lazy="selectin"
    )


class UserAchievement(Base):
    __tablename__ = "user_achievement"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    achievement_id = Column(Integer, ForeignKey(Achievement.id))
    progress = Column(Integer, default=0)
    progress_percent = Column(Float, default=0)
    is_completed = Column(Boolean, default=False)
    achievement = relationship(
        "Achievement", back_populates="user_achievements", lazy="selectin"
    )
    user = relationship("User", back_populates="user_achievements", lazy="selectin")
