import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import random
import numpy as np
import RPi.GPIO as GPIO
import time

class rainMeterApp(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("IIST Rainwater Meter")
		self.setGeometry(100,100,300,200)
		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)
		layout = QVBoxLayout(central_widget)
		self.canvas = MplCanvas()
		layout.addWidget(self.canvas)
		self.button = QPushButton("get Capacitance", self)
		layout.addWidget(self.button)
		self.button.clicked.connect(self.show_capacitance)
		self.t = []
		self.c = []
		self.max_view = 50
		self.data_x = [i for i in range(self.max_view)]
		self.data_y = [0 for i in range(self.max_view)]
		self.Vo = 26 #Switch toggle pin
		#initialising GPIO
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.Vo, GPIO.IN)
		
	def get_capacitance(self):
		val = GPIO.input(self.Vo)
		t = time.time()
		return t,val

	def show_capacitance(self):
		#QMessageBox.information(window, "Message", "Current Capacitance is:"+str(get_capacitance()))
		self.timer = self.canvas.new_timer(100)
		self.timer.add_callback(self.update_plot)
		self.timer.start()
	
	def update_plot(self):
		if len(self.data_x) > self.max_view:
			self.c.append(self.data_y[0])
			self.data_y = self.data_y[1:]
		else:
			self.data_x.append(len(self.data_x)+1)
		self.data_y.append(self.get_capacitance()[1])
		self.canvas.update_plot(self.data_x, self.data_y)

class MplCanvas(FigureCanvas):
	def __init__(self):
		self.fig, self.ax = plt.subplots()
		super().__init__(self.fig)
	def update_plot(self, x, y):
		self.ax.clear()
		self.ax.plot(x, y)
		self.draw()
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = rainMeterApp()
	window.show()
	sys.exit(app.exec_())
	
	
