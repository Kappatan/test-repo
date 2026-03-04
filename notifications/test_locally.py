# test_locally.py
import sys
import os
import logging

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем всё из main.py
from main import send_daily_notifications, _fetch_managers_new_responses, settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def print_separator(title):
    """Печатает разделитель с заголовком"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_config():
    """Проверяем, что конфиг загружается правильно"""
    print_separator("TEST 1: CONFIGURATION")
    
    print(f"✅ App name: {settings.app_name}")
    print(f"✅ Debug mode: {settings.debug}")
    print(f"✅ Main API URL: {settings.main_api_base_url}")
    print(f"✅ Path: {settings.managers_new_responses_path}")
    print(f"✅ Full URL: {settings.managers_new_responses_url}")

def test_fetch():
    """Проверяем запрос к API"""
    print_separator("TEST 2: FETCH MANAGERS DATA")
    
    print("📡 Fetching data from API...")
    data = _fetch_managers_new_responses()
    
    print(f"📊 Received data for {len(data)} managers")
    
    if data:
        print("\n📋 Sample data (first manager):")
        for key, value in data[0].items():
            print(f"   • {key}: {value}")
    
    return data

def test_notifications():
    """Проверяем отправку уведомлений"""
    print_separator("TEST 3: SEND NOTIFICATIONS")
    
    print("📧 Sending notifications...\n")
    send_daily_notifications()
    
    print("\n✅ Notifications test completed")

def main():
    """Главная функция тестирования"""
    print("\n" + "🌟"*30)
    print(" NOTIFICATION SERVICE TEST SUITE ")
    print("🌟"*30)
    
    # Проверяем, запущен ли сервер
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Mock server is running\n")
        else:
            print("❌ Mock server returned unexpected status")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Mock server is NOT running!")
        print("💡 Please run 'python3 test_server.py' in another terminal first")
        return
    
    # Запускаем тесты
    test_config()
    test_fetch()
    test_notifications()
    
    print("\n" + "✅"*30)
    print(" ALL TESTS COMPLETED SUCCESSFULLY ")
    print("✅"*30 + "\n")

if __name__ == "__main__":
    main()