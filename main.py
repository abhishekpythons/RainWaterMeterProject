import RPi.GPIO as GPIO
import time
import threading

BOTTLE_PINS = [4, 17, 27, 22, 5, 6, 13]
SENSOR_PIN = 12
SPDT_REF = 16
SPDT_WATER = 20
INLET_PUMP = 23
OUTLET_PUMP = 24
INLET_SV = 26

GPIO.setmode(GPIO.BCM)


class WaterLevelSensor:
    def __init__(self):
        GPIO.setup(SENSOR_PIN, GPIO.IN)
        self.val = GPIO.input(SENSOR_PIN)
        self.high_duration = 0.0
        self.low_duration = 0.0
        self._t = time.time()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()

    def _sample(self):
        while True:
            new_val = GPIO.input(SENSOR_PIN)
            if new_val != self.val:
                elapsed = time.time() - self._t
                if self.val == GPIO.HIGH:
                    self.high_duration = elapsed
                else:
                    self.low_duration = elapsed
                self._t = time.time()
                self.val = new_val

    def get_water_level(self):
        total = self.high_duration + self.low_duration
        if total == 0:
            return 0.0
        return (self.high_duration / total) * 100


class RainwaterMeter:
    def __init__(self, selected_bottle=1):
        self.selected_bottle = selected_bottle
        self.sensor = WaterLevelSensor()
        for pin in BOTTLE_PINS:
            GPIO.setup(pin, GPIO.OUT)
        GPIO.setup(INLET_PUMP, GPIO.OUT)
        GPIO.setup(OUTLET_PUMP, GPIO.OUT)
        GPIO.setup(INLET_SV, GPIO.OUT)
        self.reset()

    def select_bottle(self, bottle_number):
        if 1 <= bottle_number <= len(BOTTLE_PINS):
            self.selected_bottle = bottle_number
        else:
            raise ValueError(f"Bottle number must be between 1 and {len(BOTTLE_PINS)}")

    def reset(self):
        for pin in BOTTLE_PINS:
            GPIO.output(pin, GPIO.HIGH)
        GPIO.output(INLET_PUMP, GPIO.HIGH)
        GPIO.output(OUTLET_PUMP, GPIO.HIGH)
            

    def get_water_level(self):
        return self.sensor.get_water_level()

    def collect_water(self):
        self.reset()
        GPIO.output(INLET_SV, GPIO.LOW)
        GPIO.output(INLET_PUMP, GPIO.LOW)
        GPIO.output(BOTTLE_PINS[self.selected_bottle - 1], GPIO.LOW)

    def cleanup(self):
        self.reset()
        GPIO.cleanup()


#if __name__ == '__main__':
#    meter = RainwaterMeter()
#    try:
#        while True:
#            meter.collect_water()
#            print(f"Water level: {meter.get_water_level():.1f}%")
#            time.sleep(1)
#    finally:
#        meter.cleanup()
