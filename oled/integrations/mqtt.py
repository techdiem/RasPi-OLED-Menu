import random
from paho.mqtt import client as mqtt_client
import settings # pylint: disable=import-error

class MqttConnection():
    """MQTT Bridge: EventBus ↔ MQTT broker"""

    def __init__(self, eventbus=None):
        self.eventbus = eventbus
        self._connect_mqtt()
        self.client.on_message = self._on_message
        self.client.loop_start()
        self.subscriptions = {}

        # Subscribe to EventBus events to publish to MQTT (EventBus → MQTT)
        if self.eventbus is not None:
            self.eventbus.subscribe("audio.volume", self._on_eventbus_volume)
            self.eventbus.subscribe("music.nowplaying", self._on_eventbus_nowplaying)
            self.eventbus.subscribe("music.playstate", self._on_eventbus_playstate)
            self.eventbus.subscribe("music.source", self._on_eventbus_source)

        # Subscribe to MQTT topics to emit back to EventBus (MQTT → EventBus)
        self.subscribe("volume/set", self._on_mqtt_volume_command)

    def _connect_mqtt(self):
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,
                                         client_id=f"{settings.MQTT_USER}-{random.randint(0,100)}")
        self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
        self.client.will_set(f"{settings.MQTT_TOPIC}/status", payload="offline", qos=2, retain=True)
        rc = self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.publish("status", "online", retain=True)
        else:
            print(f"Failed to connect, return code {str(rc)}")

    def subscribe(self, topic, callback):
        realtopic = f"{settings.MQTT_TOPIC}/{topic}"
        self.subscriptions[realtopic] = callback
        self.client.subscribe(realtopic)
        print(f"Added MQTT subscription for topic: {realtopic}")

    def _on_message(self, _client, _userdata, msg):
        if msg.topic in self.subscriptions:
            self.subscriptions[msg.topic](msg.payload.decode())

    def publish(self, topic, message, retain=False):
        result = self.client.publish(f"{settings.MQTT_TOPIC}/{topic}", message, retain=retain)
        if result[0] != 0:
            print(f"Failed to send message to topic {topic}")

    # EventBus → MQTT
    def _on_eventbus_volume(self, volume):
        if volume is not None:
            self.publish("volume/state", str(volume), retain=True)

    def _on_eventbus_nowplaying(self, playing):
        if playing is not None:
            title = playing.get("title", "")
            artist = playing.get("artist", "")
            self.publish("music/title", title, retain=True)
            self.publish("music/artist", artist, retain=True)

    def _on_eventbus_playstate(self, playstate):
        if playstate is not None:
            self.publish("music/playstate", playstate, retain=True)

    def _on_eventbus_source(self, source):
        if source is not None:
            self.publish("music/source", source, retain=True)

    # MQTT → EventBus
    def _on_mqtt_volume_command(self, raw_volume):
        try:
            volume = int(raw_volume)
            if self.eventbus is not None:
                self.eventbus.emit_threadsafe("audio.volume", volume)
            print(f"Volume set to {volume} from MQTT")
        except ValueError:
            print(f"Received invalid volume value from MQTT: {raw_volume}")
