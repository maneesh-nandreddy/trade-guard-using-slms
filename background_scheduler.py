from apscheduler.schedulers.background import BackgroundScheduler
from alert_engine.alert_engine import evaluate_alerts
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_alert_scheduler(interval_seconds: int = 300):
    """
    Starts a background scheduler to check alerts periodically.
    Default interval is 5 minutes.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=evaluate_alerts, trigger="interval", seconds=interval_seconds)
    scheduler.start()
    logger.info(f"Alert scheduler started with interval {interval_seconds}s")
    return scheduler

if __name__ == "__main__":
    # For testing standalone
    from storage.database import init_db
    init_db()
    sched = start_alert_scheduler(10)
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
