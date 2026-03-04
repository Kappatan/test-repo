# test_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработка GET запросов"""
        
        # Эндпоинт для новых откликов
        if self.path == '/api/managers/new-responses':
            self.handle_new_responses()
        
        # Эндпоинт для проверки здоровья
        elif self.path == '/health':
            self.handle_health()
        
        # Эндпоинт для пустого ответа
        elif self.path == '/api/managers/new-responses/empty':
            self.handle_empty()
        
        # Эндпоинт для некорректных данных
        elif self.path == '/api/managers/new-responses/invalid':
            self.handle_invalid()
        
        else:
            self.send_error(404, f"Endpoint {self.path} not found")
    
    def handle_new_responses(self):
        """Отправляет тестовые данные с новыми откликами"""
        mock_data = [
            {
                "manager_id": 1,
                "manager_name": "Иван Петров",
                "manager_email": "ivan.petrov@company.ru",
                "new_responses": 5
            },
            {
                "manager_id": 2,
                "manager_name": "Мария Сидорова",
                "manager_email": "maria.sidorova@company.ru",
                "new_responses": 2
            },
            {
                "manager_id": 3,
                "manager_name": "Алексей Иванов",
                "manager_email": "alexey.ivanov@company.ru",
                "new_responses": 0
            },
            {
                "manager_id": 4,
                "manager_name": "Елена Козлова",
                "manager_email": "elena.kozlova@company.ru",
                "new_responses": 7
            },
            {
                "manager_id": 5,
                "manager_name": "Дмитрий Соколов",
                "manager_email": "dmitry.sokolov@company.ru",
                "new_responses": "3"  # Строка вместо числа - тест конвертации
            }
        ]
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(mock_data, ensure_ascii=False).encode('utf-8'))
        
        logging.info(f"✅ Sent mock data for {len(mock_data)} managers")
    
    def handle_empty(self):
        """Отправляет пустой список"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps([]).encode())
        
        logging.info("✅ Sent empty list")
    
    def handle_invalid(self):
        """Отправляет некорректные данные"""
        invalid_data = {
            "error": "Internal Server Error",
            "message": "Something went wrong"
        }
        
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(invalid_data).encode())
        
        logging.info("❌ Sent invalid data (500 error)")
    
    def handle_health(self):
        """Проверка здоровья сервера"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "healthy"}).encode())
        
        logging.info("✅ Health check requested")
    
    def log_message(self, format, *args):
        """Переопределяем логирование для чистоты вывода"""
        logging.info(f"{self.address_string()} - {format % args}")

def run_server(port=8000):
    """Запуск тестового сервера"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockAPIHandler)
    
    print("\n" + "="*60)
    print("🚀 MOCK API SERVER STARTED")
    print("="*60)
    print(f"📍 Server running on: http://localhost:{port}")
    print("\n📡 Available endpoints:")
    print(f"   ✅ GET http://localhost:{port}/api/managers/new-responses")
    print(f"   ✅ GET http://localhost:{port}/api/managers/new-responses/empty")
    print(f"   ✅ GET http://localhost:{port}/api/managers/new-responses/invalid")
    print(f"   ✅ GET http://localhost:{port}/health")
    print("\n📝 Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        httpd.shutdown()
        print("✅ Server stopped")

if __name__ == '__main__':
    run_server()