import requests


API_KEY = "26a600e49f181d86c67b07519bc3064a"  
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city_name):
    params = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"  # "metric" = Celsius, "imperial" = Fahrenheit
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        # Check if city is found
        if data.get("cod") != 200:
            print("Error:", data.get("message", "Unknown error"))
            return

        city = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        weather_desc = data["weather"][0]["description"].title()

        print(f"\nWeather in {city}, {country}:")
        print(f"  Condition : {weather_desc}")
        print(f"  Temperature : {temp}°C (feels like {feels_like}°C)")
        print(f"  Humidity : {humidity}%")

    except requests.exceptions.RequestException as e:
        print("Network error:", e)


def main():
    print("=== Simple Weather App ===")
    city = input("Enter city name: ").strip()

    if not city:
        print("City name cannot be empty.")
        return

    get_weather(city)


if __name__ == "__main__":
    main()
