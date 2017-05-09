#!/usr/bin/python
# -*- mode: python -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqldb://root:ILF@localhost/ilovefestivals', convert_unicode=True, echo=False)
Base = declarative_base()
Base.metadata.reflect(engine)

from sqlalchemy.orm import relationship, backref

class Artistes(Base):
    __table__ = Base.metadata.tables['artistes']

class Artistesfavuser(Base):
    __table__ = Base.metadata.tables['artistefavuser']

class Artistestyles(Base):
    __table__ = Base.metadata.tables['artistestyles']

class Festival(Base):
    __table__ = Base.metadata.tables['festival']

class Festivalfavuser(Base):
    __table__ = Base.metadata.tables['festivalfavuser']

class Festivalstyles(Base):
    __table__ = Base.metadata.tables['festivalstyles']

class Noteartisteuser(Base):
    __table__ = Base.metadata.tables['noteartisteuser']

class Notefestivaluser(Base):
    __table__ = Base.metadata.tables['notefestivaluser']

class Programmation(Base):
    __table__ = Base.metadata.tables['programmation']

class Style(Base):
    __table__ = Base.metadata.tables['style']

class User(Base):
    __table__ = Base.metadata.tables['user']


if __name__ == '__main__':
    from sqlalchemy.orm import scoped_session, sessionmaker, Query
    db_session = scoped_session(sessionmaker(bind=engine))
    for item in db_session.query(Style.idStyle, Style.NomStyle):
        print item

