import models
from database import engine, SessionLocal
from fastapi import FastAPI, Depends, BackgroundTasks
import uuid
from report import generate_report, get_report_status, get_report_data
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
import uvicorn
import logging

log = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Monitoring Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@app.post("/trigger_report")
async def trigger_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        report_id = str(uuid.uuid4())
        background_tasks.add_task(generate_report, db, report_id)
        return JSONResponse(content={"report_id": report_id, "status": "running"}, status_code=201)
    except Exception as e:
        log.exception(e)
        return JSONResponse(content={"message": "Something went wrong try after sometime"}, status_code=500)


@app.get('/get_report/{report_id}')
async def get_report(report_id: str, db: Session = Depends(get_db)):
    try:
        report_status = get_report_status(db, report_id)
        if not report_status:
            return JSONResponse(content={"message": "Invalid report ID"}, status_code=400)

        if report_status == 'Running':
            return JSONResponse(content={"status": "running"}, status_code=200)
        elif report_status == 'Complete':
            report_data = get_report_data(db, report_id)
            if report_data:
                return Response(content=report_data, media_type="text/csv")
            else:
                return JSONResponse(content={"message": "Failed to retrieve report data"}, status_code=400)
        else:
            return JSONResponse(content={"message": "Invalid status"}, status_code=400)

    except Exception as e:
        log.exception(e)
        return JSONResponse(content={"message": "Something went wrong, kindly try after sometime"}, status_code=500)

if __name__=="__main__":
    uvicorn.run(app, port=8001)


