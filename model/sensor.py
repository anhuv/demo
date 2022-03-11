from sqlalchemy import Boolean, Column, ForeignKey, Numeric, Integer, String, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship

from database.database import Base

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    profile = Column(String)
    longitude = Column(Float)
    latitude = Column(Float)
    created_date = Column(DateTime())
    records = relationship("Record", backref="parent", passive_deletes=False)
