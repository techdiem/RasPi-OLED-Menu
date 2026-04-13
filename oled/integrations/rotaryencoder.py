""" Rotary encoder setup """
import settings # pylint: disable=import-error

if settings.EMULATED:
    import pygame
    from integrations.emulator import emulator


class RotaryEncoder():
    _devices = []

    def __init__(self, loop, turn_callback, push_callback):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback

        if settings.EMULATED:
            emulator.event_subscribers.append(self._poll_pygame_keys)
            print("Polling PyGame keys")
        else:
            self._setup_gpiozero(settings.PIN_CLK, settings.PIN_DT, settings.PIN_SW)
            print("Using gpiozero rotary input")

    def _setup_gpiozero(self, clk_pin, dt_pin, sw_pin):
        try:
            from gpiozero import RotaryEncoder as GPIOZeroRotaryEncoder, Button
        except ImportError as exc:
            raise RuntimeError("gpiozero is required for hardware rotary input") from exc

        encoder = GPIOZeroRotaryEncoder(a=clk_pin, b=dt_pin, max_steps=0, wrap=False)
        button = Button(sw_pin, pull_up=True, bounce_time=0.05)

        encoder.when_rotated_clockwise = lambda: self.turn_callback(1)
        encoder.when_rotated_counter_clockwise = lambda: self.turn_callback(-1)
        button.when_pressed = self.push_callback

        RotaryEncoder._devices.extend([encoder, button])

    async def _poll_pygame_keys(self, event):
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.turn_callback(1)
            elif event.key == pygame.K_LEFT:
                self.turn_callback(-1)
            elif event.key == pygame.K_SPACE:
                self.push_callback()


    @staticmethod
    def cleanup():
        print("Cleaning up GPIO input")
        if not settings.EMULATED:
            for dev in RotaryEncoder._devices:
                try:
                    dev.close()
                except AttributeError:
                    pass
            RotaryEncoder._devices = []
