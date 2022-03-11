from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.sqltypes import String
from model import sensor as models
from model.record import Record
from model.sensor import Sensor 
from fastapi.templating import Jinja2Templates
from database.database import SessionLocal, engine
from pydantic import BaseModel 
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from datetime import datetime
from sqlalchemy import desc

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class SensorRequest(BaseModel):
    name: str
    created_date: Optional[datetime] = datetime.now()
    profile: Optional[str] = "default"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

templates = Jinja2Templates(directory="views")

route = APIRouter() 
@route.get("/")
def list_sensor_node(request: Request, forward_pe = None, dividend_yield = None, id_sensor = None, ma200 = None, db: Session = Depends(get_db)):

    sensor = db.query(models.Sensor)
    
    sensors = sensor.all()

    return templates.TemplateResponse("sensor.html", {
        "request": request, 
        "sensors": sensors, 
        "dividend_yield": dividend_yield,
        "lastest": None,
        "active_page_sensor": True,
        "id_sensor": id_sensor
    })


@route.put("/edit/{id_sensor}")
async def edit_sensor(id_sensor:int, sensor_request: SensorRequest, db: Session = Depends(get_db)):

    s = db.query(models.Sensor).filter(models.Sensor.id == id_sensor).first()
    s.name = sensor_request.name
    s.latitude = sensor_request.latitude
    s.longitude = sensor_request.longitude
    db.add(s)
    db.commit()

    return {
        "code": "success",
        "message": "record was edited to the database"
    }

@route.delete("/delete/{id_sensor}")
async def delete_sensor(id_sensor:int, db: Session = Depends(get_db)):
    db.query(models.Record).filter(Record.sensor_id==id_sensor).delete()
    s = db.query(models.Sensor).filter(models.Sensor.id == id_sensor).first()
    db.delete(s)
    db.commit()

    return {
        "code": "success",
        "message": "record was deleted to the database"
    }

@route.post("/create")
async def create_sensor(sensor_request: SensorRequest, db: Session = Depends(get_db)):

    sensor = models.Sensor()
    sensor.name = sensor_request.name
    sensor.latitude = sensor_request.latitude
    sensor.longitude = sensor_request.longitude
    sensor.created_date = datetime.now()
    sensor.profile = 'default'
    db.add(sensor)
    db.commit()

    return {
        "code": "success",
        "message": "record was added to the database"
    }


class LatestTelemetry(BaseModel):
    last_date: datetime
    key: str
    value: Optional[float] = None

@route.get("/lastest/{id_sensor}")
async def create_sensor(id_sensor: int, db: Session = Depends(get_db)):
    try:
        sen = db.query(models.Sensor).filter(models.Sensor.id == id_sensor).first()
        sensor_name = sen.name 
        s = db.query(models.Record).filter(models.Record.sensor_id == id_sensor).order_by(desc(models.Record.date_updated)).all()
        check = [True, True, True, True, True]
        res = []
        for i in s:
            if i.temperature != None and check[0]:
                res.append(LatestTelemetry(last_date = i.date_updated, key = 'Temperature (°C)', value = i.temperature))
                check[0] = False
            if i.humidity != None and check[1]:
                res.append(LatestTelemetry(last_date = i.date_updated, key = 'Humidity (%)', value = i.humidity))
                check[1] = False
            if i.ph != None and check[2]:
                res.append(LatestTelemetry(last_date = i.date_updated, key = 'PH', value = i.ph))
                check[2] = False
            if i.pm10 != None and check[3]:
                res.append(LatestTelemetry(last_date = i.date_updated, key = 'PM10 (µg/m³)', value = i.pm10))
                check[3] = False
            if i.pm2_5 != None and check[4]:
                res.append(LatestTelemetry(last_date = i.date_updated, key = 'PM2.5 (µg/m³)', value = i.pm2_5))
                check[4] = False
            if sum(check) ==  0:
                break
        return {
            "sensor_name": sensor_name,
            "lastest": res,
            "message": "Success"
        }
    except:
        return {
            "lastest": None,
            "message": "No information"
        }
    
    