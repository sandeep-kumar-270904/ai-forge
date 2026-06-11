import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete
from app.core.database import SessionLocal
from app.models.observability import AgentRun

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def prune_old_telemetry():
    """
    Deletes AgentRuns (and cascading AgentSpans) older than 90 days
    to prevent the PostgreSQL database from exhausting disk space.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    logger.info(f"Starting telemetry pruning cron. Deleting runs older than {cutoff_date.isoformat()}")

    async with SessionLocal() as db:
        try:
            # Due to the cascade="all, delete-orphan" on AgentRun.spans, 
            # deleting the Run will safely delete the associated Spans.
            stmt = delete(AgentRun).where(AgentRun.started_at < cutoff_date)
            result = await db.execute(stmt)
            await db.commit()
            logger.info(f"Telemetry pruning complete. Deleted {result.rowcount} old agent runs.")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error during telemetry pruning: {str(e)}")

def start_scheduler():
    # Run once a day at midnight UTC
    scheduler.add_job(prune_old_telemetry, "cron", hour=0, minute=0)
    scheduler.start()
    logger.info("APScheduler started successfully. Telemetry pruning scheduled.")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler shutdown successfully.")
