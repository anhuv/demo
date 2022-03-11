from sqlalchemy import Boolean, Column, ForeignKey, Numeric, Integer, String, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship

from database.database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Numeric(10, 2))
    humidity = Column(Numeric(10, 2))
    ph = Column(Numeric(10, 2))
    pm10 = Column(Numeric(10, 2))
    pm2_5 = Column(Numeric(10, 2))
    date_updated = Column(DateTime())
    sensor_id = Column(Integer, ForeignKey("sensors.id", ondelete='CASCADE'))