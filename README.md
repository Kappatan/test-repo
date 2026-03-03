## Recruitment Microservices

Тестовый проект с тремя микросервисами для системы подбора персонала:

- `api/` — основной API для фронтенда менеджеров
- `integration-hh/` — приём webhook-ов от HeadHunter и отправка откликов в RabbitMQ
- `notifications/` — ежедневные уведомления менеджерам о новых откликах

### Что реализовано

- основной API на FastAPI
  - регистрация и вход по JWT
  - CRUD-операции по вакансиям (редактирование только своих)
  - просмотр откликов по вакансии и смена статуса
  - endpoint для получения количества новых откликов
  - внутренний endpoint для сервиса уведомлений
  - фоновый consumer RabbitMQ, который сохраняет новые отклики в PostgreSQL
- сервис интеграции с HeadHunter (`integration-hh/`)
  - `POST /webhook/hh` с заголовком `X-API-Key`
  - псевдо-запрос к API HH для получения резюме
  - отправка данных в очередь `hh.responses` без дубликатов
- сервис ежедневных уведомлений (`notifications/`)
  - планировщик на APScheduler
  - запуск задачи по будням в 8:00 по Москве
  - запрос в основной API `/internal/managers/new-responses`
  - формирование текста письма и вывод в консоль

### Структура

```text
api/
  main.py
  config.py
  api/
    routers/
    schemas/
  services/
  repositories/

integration-hh/
  main.py
  config.py
  schemas.py

notifications/
  main.py
  config.py
```

### Быстрый старт

```bash
docker compose up --build
```

После запуска:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- RabbitMQ UI: `http://localhost:15672`
- Integration HH: `http://localhost:8001`

### Формат сообщения для RabbitMQ

Сообщение должно попадать в очередь `hh.responses`:

```json
{
  "vacancy_id": 1,
  "external_response_id": "resp-001",
  "first_name": "Ivan",
  "middle_name": "Ivanovich",
  "last_name": "Petrov",
  "contacts": [
    {
      "type": "email",
      "value": "ivan.petrov@example.com"
    }
  ]
}
```
