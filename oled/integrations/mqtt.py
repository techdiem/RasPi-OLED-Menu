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
                print(f"Failed to connect, return code {rc[0]}")

        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=f"{settings.MQTT_USER}-{random.randint(0,100)}")
        self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
        self.client.on_connect = on_connect
        self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)

    def subscribe(self, topic, callback):
        self.subscriptions[topic] = callback
        self.client.subscribe(f"{settings.MQTT_TOPIC}/{topic}")

    def _on_message(self, client, userdata, msg):
        if msg.topic in self.subscriptions:
            self.subscriptions[msg.topic](msg.payload.decode())
    
    def publish(self, topic, message):
        result = self.client.publish(topic, message)
        if result[0] != 0:
            print(f"Failed to send message to topic {topic}")

mqttclient = MqttConnection()
