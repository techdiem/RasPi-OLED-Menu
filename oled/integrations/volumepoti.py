""" ADS1115 and potentiometer setup """
import asyncio
import settings # pylint: disable=import-error
try:
    #Only available on raspberry
    import ADS1x15
except:
    pass

class VolumePoti():
    def __init__(self, loop, musicmanager) -> None:
        self.loop = loop
        self.old_val = 0
        self.musicmanager = musicmanager

        if not settings.EMULATED:
            self._setup_ads()
            self.loop.create_task(self._poll_poti_val())

    def _setup_ads(self):
        self._ADS = ADS1x15.ADS1115(1, settings.ADS_I2C)
        self._ADS.setGain(self._ADS.PGA_4_096V)
        self._ADS.setDataRate(self._ADS.DR_ADS111X_128)
        self._ADS.setMode(self._ADS.MODE_CONTINUOUS)
        self._ADS.requestADC(0) #Initial read to trigger continuous

    async def _poll_poti_val(self):
        voltage = self.ADS.toVoltage(self._ADS.getValue())
        difference = voltage - self.old_val
        self.old_val = voltage
        
        if difference > 0.1 or difference < -0.1:
            newvolume = round(voltage/0.033)
            print(f"Setting volume to {newvolume}%")
            self.musicmanager.volume = newvolume

        asyncio.sleep(0.1)
