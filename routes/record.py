from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from model import record as models
from model.sensor import Sensor 
from model.record import Record
from fastapi.templating import Jinja2Templates
from database.database import SessionLocal, engine
from pydantic import BaseModel 
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="views")

class StockRequest(BaseModel):
    symbol: str



class RecordRequest(BaseModel):
    # id: int
    temperature: Optional[float]
    humidity: Optional[float]
    ph: Optional[float]
    pm10_0: Optional[float]
    pm2_5: Optional[float]
    date_updated: Optional[datetime] = None
    sensor_id: Optional[float] = 1
    
route = APIRouter() 
@route.get("/")
def home(request: Request, sensor_id: Optional[int] = None, from_date = None, to_date = None, ma50 = None, ma200 = None, db: Session = Depends(get_db)):

    if sensor_id == None:
        stocks = db.query(Record)
    else:
        stocks = db.query(Record).filter(models.Record.sensor_id == sensor_id)

    if from_date:
        stocks = stocks.filter(Record.date_updated > from_date)

    if to_date:
        stocks = stocks.filter(Record.date_updated < to_date)
    temList = temTime = []
    stocks = stocks.all()
    if sensor_id != None:
        try:
            sensor_name = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first().name
            tem = db.query(Record).filter(Record.sensor_id == sensor_id and Record.temperature != None).all()
            temList = [x.temperature for x in tem]
            temTime = [x.date_updated for x in tem]
        except:
            raise HTTPException(status_code=404, detail="Item not found")
        
    else: sensor_name = ''
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "records": stocks, 
        "from_date": from_date,
        "to_date": to_date,
        "ma200": ma200,
        "active_page_home": True,
        "sensor_name": sensor_name,
        "temList":temList,
        "temTime":temTime,
    })




def get_record( record_id: int, db: Session = Depends(get_db)):
    return db.query(models.Record).filter(models.Record.id == record_id).first()

@route.put("/record/{id}")
def update_record(
    id: int,
    record_request: RecordRequest,
    db: Session = Depends(get_db),
    
):
    rc = get_record(db=db, record_id=id)
    rc.temperature = record_request.temperature
    rc.humidity = record_request.humidity
    rc.ph = record_request.ph
    rc.date_updated = record_request.date_updated
    rc.sensor_id = record_request.sensor_id
    rc.pm10 = record_request.pm10_0
    rc.pm2_5 = record_request.pm2_5
    db.commit()
    db.refresh(rc)
    return rc

@route.delete("/record/{id}")
async def delete_record(id: int, db: Session = Depends(get_db)):

    db.query(models.Record).filter(models.Record.id == id).delete()
    db.commit()

    return {"message": f"successfully deleted post with id: {id}"}


@route.post("/add_record")
async def add_record(record_request: RecordRequest, db: Session = Depends(get_db)):

    record = Record()
    record.temperature = record_request.temperature
    if ( record_request.date_updated == None):
        record.date_updated = datetime.now()
    else:
        record.date_updated = record_request.date_updated
    record.humidity = record_request.humidity
    record.ph = record_request.ph
    record.sensor_id = record_request.sensor_id
    record.pm10 = record_request.pm10_0
    record.pm2_5 = record_request.pm2_5
    db.add(record)
    db.commit()

    return {
        "code": "success",
        "message": "record was added to the database"
    }

