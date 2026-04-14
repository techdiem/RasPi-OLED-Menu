import math
import select
import threading
import settings # pylint: disable=import-error
if not settings.EMULATED:
    import alsaaudio

# Access to alsa mixers adapted from
# https://github.com/mopidy/mopidy-alsamixer/blob/main/mopidy_alsamixer/mixer.py

class AlsaMixer():
    def __init__(self, eventbus=None):
        self.eventbus = eventbus
        self.card = settings.ALSA_CARD
        self.mixer = settings.ALSA_MIXER
        self._last_volume = None
        self._emulated_volume = 0
        self.min_volume = settings.ALSA_VOL_MIN
        self.max_volume = settings.ALSA_VOL_MAX

        # Subscribe to volume change events from EventBus
        if self.eventbus is not None:
            self.eventbus.subscribe("audio.volume", self._on_volume_event)

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
        self._observer = AlsaMixerObserver(device=self.card, control=self.mixer, 
                                           callback=self.trigger_events_for_changed_values)
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
        current_volume = self.get_volume()
        if current_volume == volume:
            return True

        if settings.EMULATED:
            print(f"EMULATED: Set ALSA volume to {volume}")
            self._emulated_volume = volume
            self.trigger_events_for_changed_values()
        else:
            self._mixer.setvolume(self.volume_to_mixer_volume(volume))
        return True

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
            if self.eventbus is not None:
                self.eventbus.emit_threadsafe("audio.volume", self._last_volume)

    def _on_volume_event(self, volume):
        """Handle volume change events from external sources (VolumePoti, AirPlay)"""
        if volume is None:
            return
        self.set_volume(volume)


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
