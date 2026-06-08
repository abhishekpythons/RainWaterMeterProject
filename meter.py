import RPi.GPIO as gpio
import time

SPDT1 = 16
SPDT2 = 20
SEN = 12

gpio.setmode(gpio.BCM)
gpio.setup(SPDT1, gpio.OUT)
gpio.setup(SPDT2, gpio.OUT)
gpio.setup(SEN, gpio.IN)

t = None
freq = 0

def edge(pin):
  global t
  now = time.time()
  if t:
    freq = 1/(now-t)
  t = now

gpio.add_event_detect(SEN, gpio.RISING, callback=edge)
select = 0

while 1:
  select = not select
  if select:
    gpio.output(SPDT1, gpio.HIGH)
    gpio.output(SPDT2, gpio.LOW)
    print("SPDT1")
  else:
    gpio.output(SPDT1, gpio.LOW)
    gpio.output(SPDT2, gpio.HIGH)
    print("SPDT2")
  #ratio = freq[1] / freq[0] if freq[0] else 0
  print(f"freq: {freq:.2f} Hz")
  time.sleep(1)


