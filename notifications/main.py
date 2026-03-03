from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _fetch_managers_new_responses() -> list[dict[str, Any]]:
    """Запрашивает у основного API количество новых откликов по менеджерам."""
    try:
        response = requests.get(settings.managers_new_responses_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            logger.error("Unexpected response format: %s", data)
            return []
        return [item for item in data if isinstance(item, dict)]
    except Exception:
        logger.exception("Failed to fetch managers new responses from main API.")
        return []


def send_daily_notifications() -> None:
    """Формирует и «отправляет» письма менеджерам (вывод в консоль)."""
    managers = _fetch_managers_new_responses()
    if not managers:
        logger.info("No managers data received for notifications.")
        return

    for manager in managers:
        new_responses = int(manager.get("new_responses", 0))
        if new_responses <= 0:
            continue

        name = manager.get("manager_name") or "коллега"
        email = manager.get("manager_email") or "unknown"

        text = (
            f"Здравствуйте, {name}! "
            f"У вас {new_responses} новых откликов, требующих обработки."
        )

        # Имитация отправки письма — логируем в консоль.
        print(f"[EMAIL to {email}] {text}")
        logger.info("Notification printed for manager_id=%s", manager.get("manager_id"))


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    moscow_tz = ZoneInfo("Europe/Moscow")
    scheduler = BlockingScheduler(timezone=moscow_tz)

    # Пн–Пт, 8:00 по Москве
    trigger = CronTrigger(day_of_week="mon-fri", hour=8, minute=0, timezone=moscow_tz)
    scheduler.add_job(
        send_daily_notifications,
        trigger=trigger,
        name="daily_manager_notifications",
    )

    logger.info(
        "Notifications scheduler started. First run on next weekday at 08:00 Europe/Moscow."
    )

    # Для локальной отладки можно вызвать один раз сразу:
    if settings.debug:
        logger.info("DEBUG mode is ON, sending notifications immediately for test.")
        send_daily_notifications()

    scheduler.start()


if __name__ == "__main__":
    main()

