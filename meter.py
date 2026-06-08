import RPi.GPIO as gpio
import time

SPDT1 = 20
SPDT2 = 21
SEN = 12

gpio.setmode(gpio.BCM)
gpio.setup(SPDT1, gpio.OUT)
gpio.setup(SPDT2, gpio.OUT)
gpio.setup(SEN, gpio.IN)

t = None
freq = 0

def edge(pin):
  global t, freq
  now = time.time()
  if t:
    freq = 1/(now-t)
  t = now

gpio.add_event_detect(SEN, gpio.RISING, callback=edge)
select = 0

i = 0

while 1:
  i+=1
  #if i>10:
  select = not select
  #  i=0
  if select:
    gpio.output(SPDT1, gpio.LOW)
    gpio.output(SPDT2, gpio.LOW)
    print("SPDT1")
    time.sleep(3)
  else:
    gpio.output(SPDT1, gpio.HIGH)
    gpio.output(SPDT2, gpio.LOW)
    print("SPDT2")
    time.sleep(3)
  #ratio = freq[1] / freq[0] if freq[0] else 0
  print(f"freq: {freq:.2f} Hz")
  time.sleep(3)


