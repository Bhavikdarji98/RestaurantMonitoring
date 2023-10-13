from models import Report, Store
from datetime import datetime
import json
from store import calculate_uptime
import logging

log = logging.getLogger(__name__)
def generate_report(db, report_id):
    try:
        # Create new report
        report = Report(report_id=report_id, status='Running', data='')
        db.add(report)
        db.commit()

        # Generate report data
        report_data = []
        batch_size = 1000  # Process data in batches of 1000 records
        offset = 0
        stores = db.query(Store).count()
        while offset < stores:
            current_batch = db.query(Store).offset(offset).limit(batch_size).all()
            for store in current_batch:
                uptime, downtime = calculate_uptime(db, store.id)
                report_data.append({
                    'store_id': store.id,
                    'status': store.status,
                    'uptime': round(uptime, 2),
                    'downtime': round(downtime, 2)
                })
            offset += batch_size

        # Mark as completed
        print("*"*100)
        report.status = 'Complete'
        report.completed_at = datetime.utcnow()
        report.data = json.dumps(report_data)
        db.commit()

        return report
    except Exception as e:
        # Handle exceptions here
        log.exception(e)

def get_report_data(db, report_id):
    report = db.query(Report).filter_by(report_id=report_id).first()

    if report is None:
        raise ValueError(f"No report found for report_id: {report_id}")

    return report.data

def get_report_status(db, report_id):
    report = db.query(Report).filter_by(report_id=report_id).first()
    if report is None:
        return None
    else:
        return report.status