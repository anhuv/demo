from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routes import sensor, record


app = FastAPI()



# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")




app.include_router(
    record.route,
    prefix="",
    tags=["Record"]
)



app.include_router(
    sensor.route,
    prefix="/sensor",
    tags=["sensor"]
)


