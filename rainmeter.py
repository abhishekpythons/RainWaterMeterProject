import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

BOTTLE_PINS = [4, 17, 27, 22, 5, 6, 13]


class RainwaterMeter:
    def __init__(self, selected_bottle=1):
        self.selected_bottle = selected_bottle
        for pin in BOTTLE_PINS:
            GPIO.setup(pin, GPIO.OUT)
        self.reset()

    def select_bottle(self, bottle_number):
        if 1 <= bottle_number <= len(BOTTLE_PINS):
            self.selected_bottle = bottle_number
        else:
            raise ValueError(f"Bottle number must be between 1 and {len(BOTTLE_PINS)}")

    def reset(self):
        for pin in BOTTLE_PINS:
            GPIO.output(pin, GPIO.HIGH)

    def get_water_level(self):
        pass

    def collect_water(self):
        self.reset()
        GPIO.output(BOTTLE_PINS[self.selected_bottle - 1], GPIO.LOW)

    def cleanup(self):
        self.reset()
        GPIO.cleanup()


if __name__ == '__main__':
    meter = RainwaterMeter()
    try:
        meter.collect_water()
    finally:
        meter.cleanup()