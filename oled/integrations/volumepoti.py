""" ADS1115 and potentiometer setup """
import asyncio
import math
import select
import threading
import settings # pylint: disable=import-error
try:
    #Only available on raspberry
    import ADS1x15
except:
    pass
from integrations.mqtt import mqttclient
if not settings.EMULATED:
    import alsaaudio
else:
    from integrations.emulator import emulator
    import pygame

class VolumePoti():
    def __init__(self, loop, musicmanager, alsacontroller) -> None:
        self.loop = loop
        self.old_voltage = 0
        self.musicmanager = musicmanager
        self.alsacontroller = alsacontroller

        if settings.EMULATED:
            emulator.event_subscribers.append(self._poll_pygame_keys)
            print("Add volume poti subscriber for pygame events")
            #Simulating value as a starting point
            self.old_voltage = 1.2
            self._process_voltage(self.old_voltage)
        else:
            self._setup_ads()
            self.loop.create_task(self._poll_poti_val())

    def _setup_ads(self):
        self._ADS = ADS1x15.ADS1115(1, settings.ADS_I2C)
        self._ADS.setGain(self._ADS.PGA_4_096V)
        self._ADS.setDataRate(self._ADS.DR_ADS111X_128)
        self._ADS.setMode(self._ADS.MODE_CONTINUOUS)
        self._ADS.requestADC(0) #Initial read to trigger continuous

    def _process_voltage(self, voltage):
        self.old_voltage = voltage
        newvolume = round(voltage/0.033)
        print(f"Setting volume to {newvolume}%")
        self.musicmanager.volume = newvolume
        self.alsacontroller.set_volume(newvolume)

    async def _poll_poti_val(self):
        while self.loop.is_running():
            voltage = self._ADS.toVoltage(self._ADS.getValue())
            difference = voltage - self.old_voltage

            if difference > 0.03 or difference < -0.03:
                self._process_voltage(voltage)
            await asyncio.sleep(0.1)
    
    async def _poll_pygame_keys(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                voltage = self.old_voltage + 0.1
                if voltage >= 0 and voltage <= 3.3:
                    self._process_voltage(voltage)
            elif event.key == pygame.K_DOWN:
                voltage = self.old_voltage - 0.1
                if voltage >= 0 and voltage <= 3.3:
                    self._process_voltage(voltage)


#Access to alsa mixers adapted from https://github.com/mopidy/mopidy-alsamixer/blob/main/mopidy_alsamixer/mixer.py

class AlsaMixer():
    def __init__(self, musicmanager):
        self.musicmanager = musicmanager
        self.card = settings.ALSA_CARD
        self.mixer = settings.ALSA_MIXER
        self._last_volume = None
        self._emulated_volume = 0
        self.min_volume = settings.ALSA_VOL_MIN
        self.max_volume = settings.ALSA_VOL_MAX

        #MQTT connection
        self.mqtt_topic_volume = "volume/state"
        mqttclient.subscribe("volume/set", self._mqtt_set_volume)

        if not settings.EMULATED:
            known_controls = alsaaudio.cards()
            try:
                known_controls = alsaaudio.mixers(device=self.card)
            except alsaaudio.ALSAAudioError:
                print("Could not find ALSA soundcard.")
                return
            if self.mixer not in known_controls:
                print("Could not find mixer control on device.")
                return

            self.on_start()

    def on_start(self):
        self._observer = AlsaMixerObserver(device=self.card, control=self.mixer, callback=self.trigger_events_for_changed_values)
        self._observer.start()
        self.trigger_events_for_changed_values()

    @property
    def _mixer(self):
        return alsaaudio.Mixer(
            device=self.card,
            control=self.mixer
        )
    
    def get_volume(self):
        if settings.EMULATED:
            return self._emulated_volume
        else:
            channels = self._mixer.getvolume()
            if not channels:
                return None
            elif channels.count(channels[0]) == len(channels):
                return self.mixer_volume_to_volume(channels[0])
            else:
                # Not all channels have the same volume
                return None
    
    def set_volume(self, volume):
        if settings.EMULATED:
            print(f"EMULATED: Set ALSA volume to {volume}")
            self._emulated_volume = volume
            #Call trigger function to update mqtt sensor and display value
            self.trigger_events_for_changed_values()
        else:
            self._mixer.setvolume(self.volume_to_mixer_volume(volume))
        mqttclient.publish(self.mqtt_topic_volume, volume)
        return True
    
    def _mqtt_set_volume(self, raw_volume):
        try:
            self.set_volume(int(raw_volume))
            print(f"Setting volume to {raw_volume} from MQTT")
        except ValueError:
            print(f"Received invalid volume value from mqtt: {raw_volume}")

    def mixer_volume_to_volume(self, mixer_volume):
        volume = mixer_volume
        volume = math.pow(10, volume / 50.0)
        return int(volume)

    def volume_to_mixer_volume(self, volume):
        mixer_volume = (
            self.min_volume
            + volume * (self.max_volume - self.min_volume) / 100.0
        )
        try:
            mixer_volume = 50 * math.log10(mixer_volume)
            return int(mixer_volume)
        except ValueError:
            print("Invalid volume log calculation, try setting ALSA_MIN_VOLUME to 1")
            return 0   

    def trigger_events_for_changed_values(self):
        old_volume, self._last_volume = self._last_volume, self.get_volume()

        if old_volume != self._last_volume:
            self.musicmanager.volume = self._last_volume
            mqttclient.publish(self.mqtt_topic_volume, self._last_volume)


class AlsaMixerObserver(threading.Thread):
    daemon = True
    name = "AlsaMixerObserver"

    def __init__(self, device, control, callback=None):
        super().__init__()
        self.running = True

        # Keep the mixer instance alive for the descriptors to work
        self.mixer = alsaaudio.Mixer(device=device, control=control)

        descriptors = self.mixer.polldescriptors()
        assert len(descriptors) == 1
        self.fd = descriptors[0][0]
        self.event_mask = descriptors[0][1]

        self.callback = callback

    def stop(self):
        self.running = False

    def run(self):
        poller = select.epoll()
        poller.register(self.fd, self.event_mask | select.EPOLLET)
        while self.running:
            try:
                events = poller.poll(timeout=1)
                if events and self.callback is not None:
                    self.callback()
            except OSError as exc:
                # poller.poll() will raise an IOError because of the
                # interrupted system call when suspending the machine.
                print(f"Ignored IO error: {exc}")
