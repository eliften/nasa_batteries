from flask import Flask, jsonify
import threading, paho.mqtt.client as mqtt, json, os
from collections import deque
from api.model import predict_soc

DEFAULT_MQTT = {
    "host": "broker.hivemq.com",
    "port": 1883,
    "topic_sub": "battery/data",
    "topic_pub": "battery/soc_pred",
    "battery_name": "DEFAULT"
}

JSON_FILE = "mqtt_config.json"

def load_mqtt_config():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r") as f:
                config = json.load(f)
                return {
                    "host": config.get("host", DEFAULT_MQTT["host"]),
                    "port": config.get("port", DEFAULT_MQTT["port"]),
                    "topic_sub": config.get("topic_sub", DEFAULT_MQTT["topic_sub"]),
                    "topic_pub": config.get("topic_pub", DEFAULT_MQTT["topic_pub"]),
                    "battery_name": config.get("battery_name", DEFAULT_MQTT["battery_name"])
                }
        except Exception as e:
            print(f"JSON okunamadı: {e}")
    return DEFAULT_MQTT

mqtt_config = load_mqtt_config()
MQTT_BROKER = mqtt_config["host"]
MQTT_PORT = mqtt_config["port"]
MQTT_TOPIC_SUB = mqtt_config["topic_sub"]
MQTT_TOPIC_PUB = mqtt_config["topic_pub"]
BATTERY_NAME = mqtt_config["battery_name"]

app = Flask(__name__)
soc_predictions = deque(maxlen=100)

@app.route("/", methods=["GET"])
def home():
    return "API ve MQTT SOC tahmin servisi çalışıyor!"

@app.route("/latest_soc", methods=["GET"])
def latest_soc():
    latest = soc_predictions[-1] if soc_predictions else None
    battery_name = BATTERY_NAME if BATTERY_NAME else "DEFAULT"
    if latest:
        return jsonify({
            "latest_soc": latest["soc"],
            "data": latest["data"],
            "battery_name": battery_name
        })
    else:
        return jsonify({
            "latest_soc": None,
            "data": None,
            "battery_name": battery_name
        })


@app.route("/all_soc", methods=["GET"])
def all_soc():
    return jsonify({"soc_history": list(soc_predictions)})

def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC_SUB)

def on_message(client, _, msg):
    try:
        data = json.loads(msg.payload.decode())
        soc = predict_soc(data)
        soc_predictions.append({
            "soc": soc,
            "data": data
        })
        client.publish(MQTT_TOPIC_PUB, json.dumps({"soc_percent": soc}))
    except Exception as e:
        print(f"Hata: {e}")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
