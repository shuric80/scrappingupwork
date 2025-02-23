import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class PType(enum.Enum):
    HOURLY = 'Hourly'
    FIX = 'Fixed-price'


class WordSearch(Base):

    __tablename__ = 'word'

    id = Column(Integer, primary_key=True)
    text = Column("Text", String, unique=True, nullable=False)

    posts = relationship("Post", backref=backref("word", cascade="delete, all"), lazy="dynamic")


class Post(Base):

    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column("Title job post", String, nullable=False)
    url = Column('URL', String, unique=True, nullable=False)
    ptype = Column('Type', Enum(PType))
    duration = Column(String)
    history = Column(String)
    posted_time = Column("Created post", String)
    tags = Column(String)
    description = Column("Description post", String)
    proposal = Column(String)
    payment = Column('Payment verified', Boolean)
    spent = Column(String)
    location = Column("Location client", String)
    price = Column(String)
    interview = Column(String)
    feedback = Column("Feedback", Float)

    word_id = Column(Integer, ForeignKey('word.id'))

    def to_json(self):
        return dict((name, str(value)) for name, value in self.__dict__.items() if not name.startswith('_'))

    def __repr__(self):
        return '<Post:{}>'.format(self.title)
