from database import Base
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Time, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    timestamp_utc = Column(DateTime)
    status = Column(String(12))

class BusinessHours(Base):
    __tablename__ = "businesshours"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    day_of_Week = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)


class TimeZone(Base):
    __tablename__ = "timezone"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    timezone_str = Column(String(20))

class Report(Base):
    __tablename__ = "report"
    id = Column(Integer, primary_key=True)
    report_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() + 'Z',
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None
        }