import requests
import schedule
import time

# Константы для Google Analytics
GA_MEASUREMENT_ID = "ВАШ_MEASUREMENT_ID"  # Замените на ваш Measurement ID
GA_API_SECRET = "ВАШ_API_SECRET"  # Замените на ваш API Secret
GA_ENDPOINT = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"

# URL для получения курса UAH/USD
EXCHANGE_RATE_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"

def get_exchange_rate():
    """Получает текущий курс UAH/USD."""
    try:
        response = requests.get(EXCHANGE_RATE_API_URL)
        response.raise_for_status()
        rates = response.json()
        for rate in rates:
            if rate['ccy'] == 'USD' and rate['base_ccy'] == 'UAH':
                return float(rate['sale'])
    except Exception as e:
        print(f"Ошибка при получении курса: {e}")
        return None

def send_event_to_ga(exchange_rate):
    """Отправляет событие в Google Analytics."""
    if exchange_rate is None:
        print("Курс не получен. Событие не отправлено.")
        return

    payload = {
        "client_id": "555",  # Используйте постоянный client_id для серверных событий
        "events": [
            {
                "name": "exchange_rate_update",
                "params": {
                    "uah_usd_rate": exchange_rate
                }
            }
        ]
    }

    try:
        response = requests.post(GA_ENDPOINT, json=payload)
        response.raise_for_status()
        print(f"Событие отправлено в GA. Курс: {exchange_rate}")
    except Exception as e:
        print(f"Ошибка при отправке события в GA: {e}")

def worker_task():
    """Основная задача воркера."""
    exchange_rate = get_exchange_rate()
    send_event_to_ga(exchange_rate)

# Планируем выполнение задачи каждые 5 минут
schedule.every(5).minutes.do(worker_task)

if __name__ == "__main__":
    print("Воркер запущен. Ожидание событий...")
    while True:
        schedule.run_pending()
        time.sleep(1)
