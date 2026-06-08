import argparse
import threading
import time
from collections import deque

import matplotlib.pyplot as plt
import RPi.GPIO as GPIO

BOTTLE_PINS = [4, 17, 27, 22, 5, 6, 13]
SENSOR_PIN = 12

GPIO.setmode(GPIO.BCM)


class WaterLevelSensor:
    def __init__(self, sample_interval=0.01, buffer_seconds=20):
        GPIO.setup(SENSOR_PIN, GPIO.IN)
        self.val = GPIO.input(SENSOR_PIN)
        self.high_duration = 0.0
        self.low_duration = 0.0
        self._t = time.time()
        self._lock = threading.Lock()
        self._history = deque(maxlen=int(buffer_seconds / sample_interval) + 10)
        self._sample_interval = sample_interval
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()

    def _sample(self):
        while True:
            new_val = GPIO.input(SENSOR_PIN)
            now = time.time()
            with self._lock:
                self._history.append((now, int(new_val == GPIO.HIGH)))
                if new_val != self.val:
                    elapsed = now - self._t
                    if self.val == GPIO.HIGH:
                        self.high_duration = elapsed
                    else:
                        self.low_duration = elapsed
                    self._t = now
                    self.val = new_val
            time.sleep(self._sample_interval)

    def get_water_level(self):
        with self._lock:
            total = self.high_duration + self.low_duration
        if total == 0:
            return 0.0
        return (self.high_duration / total) * 100

    def get_waveform(self, window_seconds=5.0):
        cutoff = time.time() - window_seconds
        with self._lock:
            samples = [(t, v) for t, v in self._history if t >= cutoff]
        if not samples:
            return [], []
        times, values = zip(*samples)
        start_time = times[0]
        return [t - start_time for t in times], list(values)


class RainwaterMeter:
    def __init__(self, selected_bottle=1):
        self.selected_bottle = selected_bottle
        self.sensor = WaterLevelSensor()
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
        return self.sensor.get_water_level()

    def collect_water(self):
        self.reset()
        GPIO.output(BOTTLE_PINS[self.selected_bottle - 1], GPIO.LOW)

    def cleanup(self):
        self.reset()
        GPIO.cleanup()


def run_meter_loop(meter, interval=1.0, stop_event=None):
    try:
        while stop_event is None or not stop_event.is_set():
            meter.collect_water()
            print(f"Water level: {meter.get_water_level():.1f}%")
            time.sleep(interval)
    except KeyboardInterrupt:
        pass


def plot_sensor_waveform(sensor, window_seconds=5.0, update_interval=0.1):
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.step([], [], where='post')
    ax.set_ylim(-0.2, 1.2)
    ax.set_xlim(0, window_seconds)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Sensor state')
    ax.set_title('Water level sensor waveform')
    ax.grid(True, linestyle='--', alpha=0.4)

    plt.show(block=False)
    try:
        while plt.fignum_exists(fig.number):
            x, y = sensor.get_waveform(window_seconds)
            if x:
                line.set_data(x, y)
                ax.set_xlim(max(0, x[-1] - window_seconds), max(window_seconds, x[-1]))
            fig.canvas.draw_idle()
            plt.pause(update_interval)
    except KeyboardInterrupt:
        pass
    finally:
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Run the rainwater meter and show debug waveform.')
    parser.add_argument('--debug', action='store_true', help='Show live sensor waveform while collecting water')
    args = parser.parse_args()

    meter = RainwaterMeter()
    stop_event = threading.Event()

    try:
        if args.debug:
            thread = threading.Thread(target=run_meter_loop, args=(meter, 1.0, stop_event), daemon=True)
            thread.start()
            plot_sensor_waveform(meter.sensor)
        else:
            run_meter_loop(meter)
    finally:
        stop_event.set()
        meter.cleanup()


if __name__ == '__main__':
    main()
