from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
from openai import OpenAI
import Webcrawler_2  # 这里就是队友写的文件
import os

Backend_1 = Flask(__name__)
CORS(Backend_1)  # 允许所有跨域请求

# 假装我们有一个 API key（放后端才安全）
amap_apiKey = os.environ.get("AMAP_API_KEY") # 你的高德API Key
openAI_apiKey = os.environ.get("OPENAI_API_KEY") # 你的ChatGPT API Key

prompt_template = """
    **Prompt:**
    \n
    \n
    Act as an environmental data scientist specializing in urban pollution analysis. Analyze the following multi-parameter dataset and provide concise insights (≈150 words) in English. Focus on correlations, anomalies, and urgent risks.
    \n
    \n
    **Input Data Structure:**
    \n
    \n
    City: [Name]
    \n
    Temperature: [Value]
    \n
    Air Quality: [Index/Level]
    \n
    PM2.5: [Value]
    \n
    PM10: [Value]
    \n
    O3: [Value]
    \n
    \n
    **Output Requirements:**
    \n
    **Location:** [City]
    \n
    **Critical Trend:** Predict dominant pollution shifts (air/water) linked to weather.
    \n
    **Anomaly Flag:** Highlight one key deviation in air OR water data with implications.
    \n
    **Source Hypothesis:** Identify a probable primary pollution source (air/water).
    \n
    **Action Priority:** Recommend one high-impact intervention.
    \n
    \n
    **Analysis Rules:**
    \n
    \n
    Integrate air/water/weather data.
    \n
    Prioritize parameters showing exceedances or abnormal ratios.
    \n
    Speculate cautiously but directly based on typical values (e.g., PM2.5/PM10 >1.5 = combustion dominance; Turbidity spike + low pH = industrial runoff).
    \n
    \n
    **Example Input:**
    \n
    City: Beijing
    \n
    Temperature: 30°C
    \n
    Air Quality: Heavily Polluted
    \n
    PM2.5: 174
    \n
    PM10: 116
    \n
    O3: 10
    """

@Backend_1.route("/get_location", methods=["POST"])
def get_location():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")

    if not lat or not lng:
        return jsonify({"error": "Lack of latitude and longitude parameters."}), 400

    # 调用高德地图逆地理编码 API
    url = "https://restapi.amap.com/v3/geocode/regeo"
    params = {
        "location": f"{lng},{lat}",   # 注意顺序：经度,纬度
        "key": amap_apiKey,
        "extensions": "base",
        "output": "json"
    }
    resp = requests.get(url, params=params)
    result = resp.json()

    # 解析高德返回的结果
    try:
        address = result["regeocode"]["addressComponent"]
    except KeyError:
        address = "Unable to locate the current address."

    return jsonify({"address": address})

@Backend_1.route("/get_quality", methods=["POST"])
def get_quality():
    data = request.get_json()
    city = data.get("city")
    result = Webcrawler_2.get_city_data(city)
    #print(result)
    return jsonify(result)

openai.api_key = openAI_apiKey

@Backend_1.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 获取前端传来的 JSON 数据
        data = request.get_json().get("enviro_data", {})
        
        # 提取用户输入的数据
        city = data.get('city', 'Unknown City')
        temperature = data.get('temperature', 0)
        air_quality = data.get('air_quality', 'Unknown')
        pm25 = data.get('pm25', 0)
        pm10 = data.get('pm10', 0)
        o3 = data.get('o3', 0)

        # 将用户输入插入到 prompt 中
        full_prompt = prompt_template \
            .replace("City: [Name]", f"City: {str(city)}") \
            .replace("Temperature: [Value]", f"Temperature: {str(temperature)}") \
            .replace("Air Quality: [Index/Level]", f"Air Quality: {str(air_quality)}") \
            .replace("PM2.5: [Value]", f"PM2.5: {str(pm25)}") \
            .replace("PM10: [Value]", f"PM10: {str(pm10)}") \
            .replace("O3: [Value]", f"O3: {str(o3)}")

        # 调用 OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in environmental data analysis."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=300
        )

        # 提取模型的回复
        reply = response.choices[0].message.content

        # 返回结果给前端
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    Backend_1.run(host="0.0.0.0", port=5000, debug=True)