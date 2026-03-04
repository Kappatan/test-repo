from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from functools import lru_cache
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "recruitment-notifications"
    debug: bool = False

    main_api_base_url: AnyHttpUrl = "http://api:8000"
    managers_new_responses_path: str = "/internal/managers/new-responses"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def managers_new_responses_url(self) -> str:
        return f"{self.main_api_base_url}{self.managers_new_responses_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Можно добавить файловый handler:
        # logging.FileHandler("notifications.log")
    ]
)

logger = logging.getLogger(__name__)
settings = get_settings()


def _fetch_managers_new_responses() -> list[dict[str, Any]]:
    """Запрашивает у основного API количество новых откликов по менеджерам."""
    url = settings.managers_new_responses_url
    logger.debug("Fetching managers new responses from %s", url)
    
    try:
        response = requests.get(
            url, 
            timeout=10,
            headers={"User-Agent": settings.app_name}
        )
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list):
            logger.error("Unexpected response format: %s. Expected list, got %s", 
                        type(data).__name__, data)
            return []
        
        # Базовая валидация структуры данных
        valid_items = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                logger.warning("Item %d is not a dict: %s", i, type(item).__name__)
                continue
            valid_items.append(item)
        
        logger.info("Successfully fetched data for %d managers", len(valid_items))
        return valid_items
        
    except requests.exceptions.Timeout:
        logger.error("Timeout while fetching managers data from %s", url)
        return []
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while fetching managers data from %s", url)
        return []
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error %s while fetching managers data", e.response.status_code)
        return []
    except requests.exceptions.RequestException as e:
        logger.error("Request error while fetching managers data: %s", e)
        return []
    except ValueError as e:
        logger.error("JSON decode error: %s", e)
        return []
    except Exception:
        logger.exception("Unexpected error while fetching managers new responses")
        return []


def send_daily_notifications() -> None:
    """Формирует и «отправляет» письма менеджерам (вывод в консоль)."""
    logger.info("Starting daily notifications job")
    
    managers = _fetch_managers_new_responses()
    if not managers:
        logger.warning("No managers data received for notifications.")
        return

    total_new_responses = 0
    managers_with_responses = 0
    notifications_sent = 0
    
    for manager in managers:
        try:
            # Безопасное получение данных с валидацией
            new_responses = manager.get("new_responses", 0)
            
            # Пробуем преобразовать в int, если это строка
            if isinstance(new_responses, str):
                try:
                    new_responses = int(new_responses)
                except ValueError:
                    logger.warning("Invalid new_responses value for manager %s: %s", 
                                 manager.get("manager_id"), new_responses)
                    continue
            
            # Пропускаем, если нет откликов
            if new_responses <= 0:
                logger.debug("Manager %s has no new responses", manager.get("manager_id"))
                continue
            
            # Получаем данные менеджера с значениями по умолчанию
            manager_id = manager.get("manager_id")
            name = manager.get("manager_name") or "коллега"
            email = manager.get("manager_email")
            
            if not manager_id:
                logger.warning("Manager record missing manager_id: %s", manager)
            
            if not email:
                logger.warning("Manager %s has no email, skipping notification", manager_id or "unknown")
                continue
            
            # Формируем и выводим письмо
            text = (
                f"Здравствуйте, {name}! "
                f"У вас {new_responses} новых откликов, требующих обработки."
            )
            
            # Имитация отправки письма
            print(f"[EMAIL to {email}] {text}")
            notifications_sent += 1
            
            logger.info(
                "Notification prepared for manager_id=%s, responses=%d, email=%s",
                manager_id, new_responses, email
            )
            
            total_new_responses += new_responses
            managers_with_responses += 1
            
        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Error processing manager data %s: %s", manager, e)
            continue
    
    # Итоговая статистика
    logger.info(
        "Daily notifications completed: %d notifications sent to %d managers "
        "with %d total new responses",
        notifications_sent, managers_with_responses, total_new_responses
    )


def main() -> None:
    """Основная функция запуска планировщика."""
    
    # Логируем информацию о запуске
    logger.info(
        "Starting %s service (debug=%s)",
        settings.app_name,
        settings.debug
    )
    logger.info("Main API URL: %s", settings.main_api_base_url)
    logger.info("Managers new responses URL: %s", settings.managers_new_responses_url)

    # Московское время
    moscow_tz = ZoneInfo("Europe/Moscow")
    
    # Настройка планировщика
    scheduler = BlockingScheduler(
        timezone=moscow_tz,
        job_defaults={
            'coalesce': True,  # Схлопывать пропущенные запуски
            'max_instances': 1,  # Только один экземпляр задачи
            'misfire_grace_time': 60 * 60  # 1 час grace time
        }
    )

    # Пн–Пт, 8:00 по Москве
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour=8,
        minute=0,
        timezone=moscow_tz
    )
    
    scheduler.add_job(
        send_daily_notifications,
        trigger=trigger,
        name="daily_manager_notifications",
        id="daily_notifications",
        replace_existing=True,
    )

    next_run = scheduler.get_job("daily_notifications").next_run_time
    logger.info(
        "Notifications scheduler started. First run: %s",
        next_run.strftime("%Y-%m-%d %H:%M:%S %Z") if next_run else "unknown"
    )

    # Для локальной отладки
    if settings.debug:
        logger.info("DEBUG mode is ON, sending test notification immediately")
        send_daily_notifications()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.exception("Scheduler error: %s", e)
        raise


if __name__ == "__main__":
    # main()
    send_daily_notifications() # не ждать 8 утра. только для тестирования
