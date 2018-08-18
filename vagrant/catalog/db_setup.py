#!/usr/bin/env python

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Collection(Base):
    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Disc(Base):
    __tablename__ = 'disc'

    mfr = Column(String(80))
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    plastic = Column(String(80))
    weight = Column(Integer)
    discType = Column(String(80))
    color = Column(String(80))
    collection_id = Column(Integer, ForeignKey('collection.id'))
    collection = relationship(Collection)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'disc_type': self.discType,
            'mfr': self.mfr,
            'name': self.name,
            'plastic': self.plastic,
            'weight': self.weight,
            'color': self.color
        }


engine = create_engine('sqlite:///discgolfcollections.db')

Base.metadata.create_all(engine)
