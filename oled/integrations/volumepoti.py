""" ADS1115 and potentiometer setup """
import asyncio
import settings # pylint: disable=import-error
try:
    #Only available on raspberry
    import ADS1x15
except:
    pass
if settings.EMULATED:
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
