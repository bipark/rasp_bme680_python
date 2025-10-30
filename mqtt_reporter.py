import os
import json
import datetime
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

class MQTTReporter:
    def __init__(self):
        load_dotenv()
        self.server = os.getenv("MQTT_SERVER")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.user = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.topic = os.getenv("MQTT_TOPIC", "bme680/data")
        self.sensor_id = os.getenv("SENSOR_ID", "raspi-bme680")
        self.sensor_location = os.getenv("SENSOR_LOCATION", "LIVINGROOM")
        self.publish_interval = int(os.getenv("PUBLISH_INTERVAL_SEC", "600"))
        self.sea_level_hpa = float(os.getenv("SEA_LEVEL_HPA", "1013.25"))
        self.client = None
        self.next_publish_ts = 0
        self.connect()
    def connect(self):
        if not self.server:
            return
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            if self.user:
                client.username_pw_set(self.user, self.password or None)
            client.connect(self.server, self.port, keepalive=60)
            client.loop_start()
            self.client = client
        except Exception as e:
            print(f"MQTT 연결 실패: {e}")
            self.client = None
    def should_publish(self):
        now = time.time()
        return self.client is not None and now >= self.next_publish_ts
    def update_publish_time(self):
        self.next_publish_ts = time.time() + self.publish_interval
    def create_payload(self, t, h, p, gas=None, altitude=None, dew_point=None):
        doc = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "sensor_id": self.sensor_id,
            "sensor_location": self.sensor_location,
            "temperature": round(t, 1),
            "humidity": round(h, 1),
            "pressure": round(p, 1),
            "gas_resistance": None if gas is None else round(gas, 1),
            "altitude": None if altitude is None else round(altitude, 1),
            "dew_point": None if dew_point is None else round(dew_point, 1),
        }
        return json.dumps(doc, ensure_ascii=False)
    def publish(self, t, h, p, gas=None, altitude=None, dew_point=None):
        payload = self.create_payload(t, h, p, gas, altitude, dew_point)
        topic = self.topic + "/" + self.sensor_id
        try:
            self.client.publish(topic, payload, qos=0, retain=False)
        except Exception as e:
            print(f"MQTT 전송 실패: {e}")
