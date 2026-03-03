Сервис интеграции с HeadHunter.

### Возможности

- принимает webhook-и HH по адресу `POST /webhook/hh`
- проверяет заголовок `X-API-Key` на совпадение с секретом из `.env`
- псевдо-обращается к API HH для получения информации о резюме
- отправляет данные об отклике в RabbitMQ в очередь `hh.responses` **без дубликатов**

### Формат webhook-а

Эндпоинт ожидает тело, схожее с [`NEW_RESPONSE_OR_INVITATION_VACANCY`](https://api.hh.ru/openapi/redoc#tag/Webhook-API/operation/post-webhook-subscription):

```json
{
  "items": [
    {
      "id": "resp-001",
      "vacancy": { "id": 1 },
      "resume": { "id": "resume-123" }
    }
  ]
}
```

Все лишние поля из реального webhook-а игнорируются.

### Сообщение в RabbitMQ

В очередь `hh.responses` отправляется сообщение вида:

```json
{
  "vacancy_id": 1,
  "external_response_id": "resp-001",
  "first_name": "Test",
  "middle_name": null,
  "last_name": "Candidate",
  "contacts": [
    { "type": "email", "value": "test.candidate@example.com" }
  ]
}
```

### Запуск локально

```bash
cd integration-hh
pip install -r requirements.txt
python main.py
```

