from __future__ import annotations

import json
import logging
from typing import Any, Final, Set

import pika
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status

from config import get_settings
from schemas import HhWebhookPayload

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

_seen_external_ids: Set[str] = set()
_SEEN_LIMIT: Final[int] = 10_000


def _remember_external_id(external_id: str) -> bool:
    """Вернёт True, если это новый id, иначе False."""
    if external_id in _seen_external_ids:
        return False

    if len(_seen_external_ids) >= _SEEN_LIMIT:
        # Простейшая стратегия очистки — сбрасываем множество.
        _seen_external_ids.clear()

    _seen_external_ids.add(external_id)
    return True


def _get_resume_info(resume_id: str) -> dict[str, Any]:
    """Псевдо-запрос к API HH для получения резюме.

    Вместо реального HTTP-запроса возвращаем заглушку и
    эмулируем возможные ошибки:
    - id == "404" -> 404 Not Found
    - id == "500" -> 502 Bad Gateway
    """
    if resume_id == "404":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found in HH.",
        )
    if resume_id == "500":
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="HH API temporary unavailable.",
        )

    # Упрощённый успешный ответ
    return {
        "first_name": "Test",
        "middle_name": None,
        "last_name": "Candidate",
        "contacts": [
            {"type": "email", "value": "test.candidate@example.com"},
        ],
    }


def _publish_to_rabbitmq(message: dict[str, Any]) -> None:
    """Отправка сообщения в RabbitMQ в очередь hh.responses."""
    parameters = pika.URLParameters(settings.rabbitmq_url)
    connection = pika.BlockingConnection(parameters)
    try:
        channel = connection.channel()
        channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
        body = json.dumps(message).encode("utf-8")
        channel.basic_publish(
            exchange="",
            routing_key=settings.rabbitmq_queue,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info("Published message to RabbitMQ: %s", message)
    finally:
        connection.close()


@app.post(
    "/webhook/hh",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Webhook для приёма откликов от HeadHunter",
)
async def hh_webhook(
    payload: HhWebhookPayload,
    request: Request,
    x_api_key: str = Header(alias="X-API-Key"),
) -> dict[str, int]:
    """Принимает webhook от HH, валидирует ключ, обогащает резюме и пишет в RabbitMQ.

    Допускаются дубли webhook-ов, но в очередь данные отправляются без дубликатов
    по полю external_response_id (используется id элемента webhook-а).
    """
    if x_api_key != settings.hh_webhook_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key.")

    accepted = 0

    for item in payload.items:
        external_id = item.id

        # Псевдо-запрос резюме с обработкой ошибок
        resume = _get_resume_info(item.resume.id)

        if not _remember_external_id(external_id):
            logger.info("Duplicate external_response_id '%s' skipped.", external_id)
            continue

        message = {
            "vacancy_id": item.vacancy.id,
            "external_response_id": external_id,
            "first_name": resume["first_name"],
            "middle_name": resume.get("middle_name"),
            "last_name": resume["last_name"],
            "contacts": resume.get("contacts") or [],
        }

        _publish_to_rabbitmq(message)
        accepted += 1

    logger.info(
        "Processed HH webhook from %s, accepted=%s",
        request.client.host if request.client else "unknown",
        accepted,
    )

    return {"accepted": accepted}


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

