import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...crud.crud_evaluation import evaluation_run, evaluation_result
from ...models.evaluation import EvaluationRun, EvaluationResult
from .judge import LLMJudge

logger = logging.getLogger(__name__)

class EvaluationWorker:
    @staticmethod
    async def run_evaluation_batch(db: AsyncSession, run_id: str):
        """
        Async worker function to process an evaluation run.
        Designed to be called via FastAPI BackgroundTasks or Celery.
        """
        run = await evaluation_run.get(db, id=run_id)
        if not run:
            logger.error(f"EvaluationRun {run_id} not found.")
            return

        run.status = "running"
        db.add(run)
        await db.commit()

        dataset = run.dataset
        rows = dataset.rows
        
        total_score = 0.0
        processed = 0

        for row in rows:
            try:
                # 1. Execute Target Agent/Prompt (Mocked for MVP)
                actual_output = {"output": "Mocked execution output"}
                latency = 120 # ms
                
                # 2. Score via LLM Judge
                score, reasoning = await LLMJudge.evaluate_output(actual_output, row.expected_output)
                
                # 3. Save Result
                result = EvaluationResult(
                    run_id=run.id,
                    row_id=row.id,
                    actual_output=actual_output,
                    score=score,
                    reasoning=reasoning,
                    latency_ms=latency,
                    cost_usd=0.001 # Simulated cost
                )
                db.add(result)
                total_score += score
                processed += 1
            except Exception as e:
                logger.error(f"Error processing row {row.id}: {e}")

        # Update Run
        run.completed_at = datetime.utcnow()
        run.status = "completed"
        run.overall_score = (total_score / processed) if processed > 0 else 0.0
        db.add(run)
        await db.commit()
        logger.info(f"EvaluationRun {run_id} completed with score {run.overall_score}")
