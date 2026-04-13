""" ADS1115 and potentiometer setup """
import asyncio
import settings # pylint: disable=import-error
try:
    #Only available on raspberry
    import ADS1x15
except (ModuleNotFoundError, FileNotFoundError):
    pass
if settings.EMULATED:
    from integrations.emulator import emulator
    import pygame

class VolumePoti():
    def __init__(self, loop, eventbus=None) -> None:
        self.loop = loop
        self.eventbus = eventbus
        self.old_voltage = 0

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
        self.ads = ADS1x15.ADS1115(1, settings.ADS_I2C)
        self.ads.setGain(self.ads.PGA_4_096V)
        self.ads.setDataRate(self.ads.DR_ADS111X_128)
        self.ads.setMode(self.ads.MODE_CONTINUOUS)
        self.ads.requestADC(0) #Initial read to trigger continuous

    def _process_voltage(self, voltage):
        self.old_voltage = voltage
        newvolume = round(voltage/0.033)
        print(f"Setting volume to {newvolume}%")
        if self.eventbus is not None:
            self.eventbus.emit_threadsafe("audio.volume", newvolume)

    async def _poll_poti_val(self):
        while self.loop.is_running():
            voltage = self.ads.toVoltage(self.ads.getValue())
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
