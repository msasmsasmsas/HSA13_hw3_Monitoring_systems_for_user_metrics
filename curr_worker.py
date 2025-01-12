import requests
import schedule
import time
import uuid

# Константы для Google Analytics
GA_MEASUREMENT_ID = "10113434014"  # Замените на ваш Measurement ID
GA_MEASUREMENT_ID = "G-KWGNW16Z4F"
GA_API_SECRET = "9_dPCD1cRMmS1VezHeGE8A"  # Замените на ваш API Secret
GA_ENDPOINT = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"

# URL для получения курса UAH/USD
#EXCHANGE_RATE_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"

# API для получения курсов валют
EXCHANGE_RATE_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

# Список стран и их валют (ISO 3166-1 alpha-2 и код валюты ISO 4217)
COUNTRIES = [
    {"country": "US", "currency": "USD", "flag": "🇺🇸", "name": "United States"},
    {"country": "CA", "currency": "CAD", "flag": "🇨🇦", "name": "Canada"},
    {"country": "GB", "currency": "GBP", "flag": "🇬🇧", "name": "United Kingdom"},
    {"country": "EU", "currency": "EUR", "flag": "🇪🇺", "name": "Eurozone"},
    {"country": "JP", "currency": "JPY", "flag": "🇯🇵", "name": "Japan"},
    {"country": "AU", "currency": "AUD", "flag": "🇦🇺", "name": "Australia"},
    {"country": "CH", "currency": "CHF", "flag": "🇨🇭", "name": "Switzerland"},
    {"country": "CN", "currency": "CNY", "flag": "🇨🇳", "name": "China"},
    {"country": "IN", "currency": "INR", "flag": "🇮🇳", "name": "India"},
    {"country": "BR", "currency": "BRL", "flag": "🇧🇷", "name": "Brazil"},
]

def fetch_exchange_rates():
    """Получает текущие курсы валют с сайта Национального Банка Украины."""
    response = requests.get(EXCHANGE_RATE_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении курсов валют: {response.status_code}")
        return []

def get_country_exchange_rate(rates, currency):
    """Извлекает курс для указанной валюты."""
    for rate in rates:
        if rate["cc"] == currency:
            return float(rate["rate"])
    return None

def send_event_to_ga4(country, currency, exchange_rate):
    """Отправляет событие в Google Analytics."""
    if exchange_rate is None:
        print(f"Курс для {country} ({currency}) не найден.")
        return

    client_id = str(uuid.uuid4())
    payload = {
        "client_id": client_id, #"currency_tracker_123",  # Уникальный идентификатор клиента
        "events": [
            {
                "name": "currency_exchange_rate",
                "params": {
                    "debug_mode": True,
                    "geo_country": country,
                    "currency": currency,
                    "exchange_rate": exchange_rate,
                }
            }
        ]
    }
    print(f"Отправка события: {payload}")
    response = requests.post(GA_ENDPOINT, json=payload)
    print(f"Ответ сервера: {response.status_code}, {response.text}")

    if response.status_code == 204:
        print(f"Событие отправлено: {country} ({currency}): {exchange_rate}")
    else:
        print(f"Ошибка отправки: {response.status_code}, ответ: {response.text}")

def track_exchange_rates():
    """Отслеживает курсы валют для каждой страны."""
    rates = fetch_exchange_rates()
    if not rates:
        return

    for country in COUNTRIES:
        exchange_rate = get_country_exchange_rate(rates, country["currency"])
        send_event_to_ga4(country["country"], country["currency"], exchange_rate)

# Планируем выполнение задачи каждые 5 секунд
schedule.every(30).seconds.do(track_exchange_rates)

if __name__ == "__main__":
    print("Трекер курсов валют запущен.")
    while True:
        schedule.run_pending()
        time.sleep(1)