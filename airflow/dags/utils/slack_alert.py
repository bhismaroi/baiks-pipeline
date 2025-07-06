"""Utility to send Slack alerts from Airflow task failures.

Exposed function `slack_alert` is imported by multiple DAGs.
If Slack connection or provider package is missing, we degrade gracefully and just log the
message so DAG parsing never fails.
"""
from __future__ import annotations

import logging
import os
from dotenv import load_dotenv

# Optional import – Airflow slack provider may not be present in the image at parse-time.
try:
    from airflow.providers.slack.operators.slack import SlackAPIPostOperator  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    SlackAPIPostOperator = None  # type: ignore

load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#alerts")
logger = logging.getLogger(__name__)

def slack_alert(context):  # type: ignore
    """Send failure alert to Slack (or log warning if not configured).

    This function is designed to be used as Airflow ``on_failure_callback``.
    It never raises to avoid breaking the DAG run.
    """
    dag_id = context.get("dag_run").dag_id if context.get("dag_run") else "unknown_dag"
    task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown_task"
    exec_date = context.get("execution_date")
    log_url = context.get("task_instance").log_url if context.get("task_instance") else ""

    text = (
        f"DAG *{dag_id}* failed on task *{task_id}*\n"
        f"Execution Date: {exec_date}\nLog: {log_url}"
    )

    if SlackAPIPostOperator and SLACK_TOKEN:
        try:
            SlackAPIPostOperator(
                task_id="slack_alert",
                token=SLACK_TOKEN,
                text=text,
                channel=SLACK_CHANNEL,
            ).execute(context)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to post Slack alert: %s", exc)
    else:
        logger.warning("Slack alert skipped – provider or token missing. Message: %s", text)