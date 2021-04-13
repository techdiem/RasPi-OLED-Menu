import asyncio
import settings

class RotaryEncoder():
    def __init__(self, loop, emulated, callback):
        self.loop = loop
        self.emulated = emulated
        self.callback = callback

        if self.emulated:
            self.loop.create_task(self._poll_pygame_keys())
        else:
            #Config for pins!
            self._setup_gpio(settings.PIN_CLK, settings.PIN_DT, settings.PIN_SW)

    def _rotary_push(self):
        pass

    def _rotary_turn(self):
        pass

    def _setup_gpio(self, clk, dt, sw):
        import RPi.GPIO as GPIO # pylint: disable=import-error
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Rotary encoder
        GPIO.add_event_detect(clk, GPIO.RISING, callback=self._rotary_turn)
        GPIO.add_event_detect(dt, GPIO.RISING, callback=self._rotary_turn)
        #Push Button
        GPIO.add_event_detect(sw, GPIO.FALLING, callback=self._rotary_push, bouncetime=300)

    async def _poll_pygame_keys(self):
        import pygame
        while self.loop.is_running():
            event = pygame.event.poll()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    self.callback()

            await asyncio.sleep(0.01)

    def cleanup(self):
        if not self.emulated:
            import RPi.GPIO as GPIO # pylint: disable=import-error
            GPIO.cleanup()
