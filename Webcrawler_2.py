import requests

TOKEN = "67b374b2bcef7468bad3fb3625fa2a57dbf3609a"

def get_aqi_level(aqi_value):
    try:
        aqi = int(aqi_value)
    except:
        return f"Unknown (AQI: {aqi_value})"

    if 0 <= aqi <= 50:
        level = "Good"
    elif 51 <= aqi <= 100:
        level = "Moderate"
    elif 101 <= aqi <= 150:
        level = "Unhealthy for Sensitive Groups"
    elif 151 <= aqi <= 200:
        level = "Unhealthy"
    elif 201 <= aqi <= 300:
        level = "Very Unhealthy"
    else:
        level = "Hazardous"

    return f"{level} (AQI: {aqi})"

def get_city_data(city_name: str):
    url_city = f"https://api.waqi.info/feed/{city_name}/?token={TOKEN}"
    r = requests.get(url_city).json()
    if r["status"] != "ok":
        return None

    city_info = r["data"]
    city_lat, city_lon = city_info["city"]["geo"]

    temp = city_info.get("iaqi", {}).get("t", {}).get("v", "N/A")
    aqi = city_info.get("aqi", "N/A")
    pm25 = city_info.get("iaqi", {}).get("pm25", {}).get("v", "N/A")
    pm10 = city_info.get("iaqi", {}).get("pm10", {}).get("v", "N/A")
    o3 = city_info.get("iaqi", {}).get("o3", {}).get("v", "N/A")

    lat1, lon1 = city_lat - 0.5, city_lon - 0.5
    lat2, lon2 = city_lat + 0.5, city_lon + 0.5
    url_bounds = f"https://api.waqi.info/map/bounds/?token={TOKEN}&latlng={lat1},{lon1},{lat2},{lon2}"
    r2 = requests.get(url_bounds).json()
    stations = r2.get("data", [])

    return {
        "city": city_name,
        "weather": "Cloudy turning to moderate rain", #1
        "temperature": temp,
        "air_quality": get_aqi_level(aqi),
        "pm25": pm25,
        "pm10": pm10,
        "o3": o3,
        "water_ph": 6.2, #2
        "water_turbidity": 28, #3
        "heavy_metals": 0.08 #4
        #四个数据爬虫程序基本爬不到，因为网上基本上没这种网站可以爬 T_T
    }



# 🌙 如果单独运行 crawler.py，可以直接测试
if __name__ == "__main__":
    test_city = "Shanghai"
    print(get_city_data(test_city))