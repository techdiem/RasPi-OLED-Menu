""" Rotary encoder setup """
import asyncio
import threading
import settings # pylint: disable=import-error
try:
    #Only avaiable on Raspberry
    import RPi.GPIO as GPIO # pylint: disable=import-error
except (ImportError, RuntimeError):
    pass

class RotaryEncoder():
    def __init__(self, loop, turn_callback, push_callback):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback

        if settings.EMULATED:
            self.loop.create_task(self._poll_pygame_keys())
            print("Polling PyGame keys")
        else:
            #Config for pins!
            self.current_clk = 1
            self.current_dt = 1
            self.lockrotary = threading.Lock() #create lock for rotary switch
            self._setup_gpio(settings.PIN_CLK, settings.PIN_DT, settings.PIN_SW)
            print("Using rotary encoder interrupts")

    def _rotary_push(self, channel):
        del channel
        self.push_callback()

    def _rotary_turn(self, channel):
        switch_a = GPIO.input(settings.PIN_CLK)
        switch_b = GPIO.input(settings.PIN_DT)

        if self.current_clk == switch_a and self.current_dt == switch_b:
            #Same interrupt as before? -> Bouncing -> no action
            pass
        else:
            #refresh saved state
            self.current_clk = switch_a
            self.current_dt = switch_b

            if (switch_a and switch_b): #both ones active
                self.lockrotary.acquire()
                if channel == settings.PIN_DT: #Direction depends on which one was last
                    self.turn_callback(1)
                else:
                    self.turn_callback(-1)
                self.lockrotary.release()

    def _setup_gpio(self, clk_pin, dt_pin, sw_pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Rotary encoder
        GPIO.add_event_detect(clk_pin, GPIO.RISING, callback=self._rotary_turn)
        GPIO.add_event_detect(dt_pin, GPIO.RISING, callback=self._rotary_turn)
        #Push Button
        GPIO.add_event_detect(sw_pin, GPIO.FALLING, callback=self._rotary_push, bouncetime=300)

    async def _poll_pygame_keys(self):
        import pygame
        while self.loop.is_running():
            event = pygame.event.poll()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.turn_callback(1)
                elif event.key == pygame.K_LEFT:
                    self.turn_callback(-1)
                elif event.key == pygame.K_SPACE:
                    self.push_callback()

            await asyncio.sleep(0.01)

    @staticmethod
    def cleanup():
        print("Cleaning up GPIO")
        if not settings.EMULATED:
            GPIO.cleanup()
