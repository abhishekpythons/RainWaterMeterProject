import gpiod
from gpiod.line import Edge, Direction, Value
import threading, time
from flask import Flask, request

CHIP = "/dev/gpiochip0"
FREQ=12
A, B = 20, 21

app = Flask(__name__)
hz = 0.0
st = {A:0, B:0}

out = gpiod.request_lines(
	CHIP,
	consumer="outs",
	config={
		A: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE),
		B: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)
	},
)

def counter():
	global hz
	with gpiod.request_lines(
		CHIP,
		consumer="freq",
		config={FREQ: gpiod.LineSettings(edge_detection=Edge.RISING)},
	) as req:
		while 1:
			n = 0
			t0 = time.perf_counter()
			while time.perf_counter() - t0 < 1.0:
				if req.wait_edge_events(timeout=0.2):
					n += len(req.read_edge_events())
			hz = n / (time.perf_counter() - t0)
				
threading.Thread(target=counter, daemon=True).start()

@app.route("/")
def home():
	return f'''
		<h2> Freq: {hz:.2f} Hz</h2>
		<p> A : {'ON' if st[A] else 'OFF'} &nbsp; <a href="/t/a">toggle A</a></p>
		<p> B : {'ON' if st[B] else 'OFF'} &nbsp; <a href="/t/b">toggle B</a></p>
		<meta http-equiv="refresh" content="1">
	'''
		
@app.route("/t/<p>")
def toggle(p):
	pin = A if p == "a" else B
	st[pin] ^= 1
	out.set_value(pin, Value.ACTIVE if st[pin] else Value.INACTIVE)
	return ("", 302, {"Location": "/"})


if __name__ == "__main__":
	app.run(host = "0.0.0.0", port=5000)

