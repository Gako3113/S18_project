import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings_secret import *

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"autoload": True}

class Trip(Base):
    __tablename__ = "trip"
    __table_args__ = {"autoload": True}

class Trip_join(Base):
    __tablename__ = "trip_join"
    __table_args__ = {"autoload": True}

class Settle(Base):
    __tablename__ = "settle"
    __table_args__ = {"autoload": True}

class Payment(Base):
    __tablename__ = "payment"
    __table_args__ = {"autoload": True}

class Payment_member(Base):
    __tablename__ = "payment_member"
    __table_args__ = {"autoload": True}

