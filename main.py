import RPi.GPIO as gpio
gpio.setmode(gpio.BCM)
bottles = [4, 17, 27, 22, 5, 6, 13]
for bottle in bottles:
    gpio.setup(bottle, gpio.OUT)
    gpio.output(bottle, gpio.HIGH)

class rainwater:
    def __init__(self, bottle=1):
        for bottle in bottles:
            gpio.setup(bottle, gpio.OUT)
        self.selected_bottle = bottle
    def change_bottle(self, bottle):
        self.selected_bottle = bottle
    def reset(self):
        for bottle in bottles:
            gpio.setup(bottle, gpio.OUT)
            gpio.output(bottle, gpio.HIGH)
    def update(self):
        self.reset()
        gpio.output(bottles[self.selected_bottle-1], gpio.LOW)

if __name__ == '__main__':
    meter = rainwater()
