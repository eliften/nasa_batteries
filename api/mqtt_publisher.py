import paho.mqtt.client as mqtt
import json, pandas as pd
import time
from utils.get_data import getData

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "battery/data"

data_path = ["data/B0006.mat", "data/B0018.mat"]

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

for d in data_path:
    g = getData(d)
    g.parse_data()
    df_feat = g.feature_eng(g.data)

    for i, row in df_feat.iterrows():
        sample = {
            "voltage_measured": float(row['voltage_measured']),
            "current_measured": float(row['current_measured']),
            "temperature_measured": float(row['temperature_measured']),
            "Q_cum_Ah": float(row['Q_cum_Ah']),
            "capacity": float(row['capacity']) if not pd.isna(row['capacity']) else None,
            "dV_dt": float(row['dV_dt'])
        }
        print(sample)

        time_s = row["dt_s"]

        client.publish(MQTT_TOPIC, json.dumps(sample))

        time.sleep(time_s)
