import random
from paho.mqtt import client as mqtt_client
import settings # pylint: disable=import-error
import ssl

class MqttConnection():
    def __init__(self):
        self._connect_mqtt()
        self.client.on_message = self._on_message
        self.client.loop_start()
        self.subscriptions = {}

    def _connect_mqtt(self):
        def on_connect(rc, *args, **kwargs):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {str(rc)}")

        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=f"{settings.MQTT_USER}-{random.randint(0,100)}")
        self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
        self.client.on_connect = on_connect
        self.client.will_set(f"{settings.MQTT_TOPIC}/status", payload="offline", qos=2, retain=True)
        self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        self.publish("status", "online", retain=True)

    def subscribe(self, topic, callback):
        realtopic = f"{settings.MQTT_TOPIC}/{topic}"
        self.subscriptions[realtopic] = callback
        self.client.subscribe(realtopic)
        print(f"Added MQTT subscription for topic: {realtopic}")

    def _on_message(self, client, userdata, msg):
        if msg.topic in self.subscriptions:
            self.subscriptions[msg.topic](msg.payload.decode())
    
    def publish(self, topic, message, retain=False):
        result = self.client.publish(f"{settings.MQTT_TOPIC}/{topic}", message, retain=retain)
        if result[0] != 0:
            print(f"Failed to send message to topic {topic}")

mqttclient = MqttConnection()
