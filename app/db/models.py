# coding: utf-8
from sqlalchemy import Column, Float, Index, Integer, Text, text, Sequence,String,ForeignKey,Date,Boolean,Enum,LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship 
from config.config import Config
Base = declarative_base()
BaseMedia = declarative_base()



# 用户信息表模型类
class Users(Base):
    __tablename__ = 'USERS'

    ID = Column(Integer,Sequence('ID'), primary_key=True)
    USERID = Column(String(50), nullable=False,unique=True)
    PHONE= Column(String(50),nullable=True)
    if Config._rsa_encrypt:
        ACCOUNT=Column(LargeBinary,nullable=True)
        PASSWORD=Column(LargeBinary,nullable=True)
    else:
        ACCOUNT=Column(String(50),nullable=True)
        PASSWORD=Column(String(50),nullable=True)        
    VERIFY=Column(Boolean,nullable=True)
    PAY_CHOICES = ('0','1', '2', '3')
    PAY=Column(Enum(*PAY_CHOICES),nullable=True)

# 用户操作信息表模型类
class UserAction(Base):
    __tablename__ = 'USERACTION'

    ID = Column(Integer, Sequence('ID'),primary_key=True)
    USERID = Column(String(50), ForeignKey('USERS.ID'))
    WEEKDAY_CHOICES=('1', '2', '3','4','5','6','7')
    WEEKDAY=Column(Enum(*WEEKDAY_CHOICES),nullable=True)
    DATE = Column(Date,nullable=True)
    GYM_CHOICES=('0', '1')
    GYM=Column(Enum(*GYM_CHOICES),nullable=True)
    FIELD=Column(String(50))
    APPOINTTIME=Column(String(500))
    STATUS=Column(Boolean,default=True)
    user = relationship("Users", backref="actions")











