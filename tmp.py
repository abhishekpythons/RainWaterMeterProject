
import RPi.GPIO as GPIO
import time

Vo = 26

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Vo, GPIO.IN)
val = GPIO.input(Vo)
t=time.time()
while 1:
  new_val = GPIO.input(Vo)
  if new_val != val:
    print(time.time()-t)
    t = time.time()
    val = GPIO.input(Vo)
