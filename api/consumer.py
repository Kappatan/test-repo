from __future__ import annotations

import json
import logging
import threading
import time

import pika

from config import get_settings
from repositories.response_repository import ResponseRepository
from repositories.session import SessionLocal
from repositories.vacancy_repository import VacancyRepository
from services.dto import ContactDTO, IngestResponseDTO
from services.response_service import ResponseService

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self.settings.rabbitmq_enabled:
            logger.info("RabbitMQ consumer is disabled.")
            return

        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()

    def _consume(self) -> None:
        while True:
            try:
                parameters = pika.URLParameters(self.settings.rabbitmq_url)
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                channel.queue_declare(queue=self.settings.rabbitmq_queue, durable=True)
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=self.settings.rabbitmq_queue,
                    on_message_callback=self._handle_message,
                )
                logger.info(
                    "RabbitMQ consumer is listening queue '%s'.",
                    self.settings.rabbitmq_queue,
                )
                channel.start_consuming()
            except Exception:
                logger.exception("RabbitMQ consumer failed. Reconnecting soon.")
                time.sleep(self.settings.rabbitmq_reconnect_delay_seconds)

    def _handle_message(self, channel, method, _properties, body: bytes) -> None:
        try:
            payload = json.loads(body.decode("utf-8"))
            contacts = payload.get("contacts") or []
            if not isinstance(contacts, list):
                raise ValueError("contacts must be a list.")

            data = IngestResponseDTO(
                vacancy_id=payload.get("vacancy_id"),
                first_name=str(payload.get("first_name", "")).strip(),
                middle_name=payload.get("middle_name"),
                last_name=str(payload.get("last_name", "")).strip(),
                contacts=[
                    ContactDTO(
                        type=str(item.get("type", "")).strip(),
                        value=str(item.get("value", "")).strip(),
                    )
                    for item in contacts
                    if isinstance(item, dict)
                ],
                external_response_id=(
                    str(payload.get("external_response_id"))
                    if payload.get("external_response_id") is not None
                    else (
                        str(payload.get("response_id"))
                        if payload.get("response_id") is not None
                        else None
                    )
                ),
            )
            session = SessionLocal()
            try:
                service = ResponseService(
                    response_repository=ResponseRepository(session),
                    vacancy_repository=VacancyRepository(session),
                )
                created = service.ingest_from_queue(data)
                if created:
                    logger.info("Response %s has been saved.", data)
                else:
                    logger.info("Response %s was skipped.", data)
            finally:
                session.close()
        except json.JSONDecodeError:
            logger.exception("Invalid RabbitMQ payload.")
        except Exception:
            logger.exception("Failed to process RabbitMQ message.")
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)
