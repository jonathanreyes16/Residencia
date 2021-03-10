from flask import Flask
import requests 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from skfuzzy import control as ctrl
from sklearn.metrics import mean_absolute_error
from time import process_time
from timeit import default_timer as timer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
import skfuzzy as fuzzy
data_frecuencia = None
data_saturacion = None

app = Flask(__name__)

@app.route('/dato/<freq>_<sat>')
def main(freq,sat):

	#getCSV()
	#plotCSV()
	showFuzzy()
	#movingMedianGraphSpO2()
	#movingMedianGraphHR()
	#movilFuzzy()

def setValores(freq,sat):
	global data_saturacion
	global data_frecuencia
	data_saturacion = sat
	data_frecuencia = freq
	print("----------------------------------------------------------------------------------------------------")
	print('Saturacion : ',data_saturacion) #promedios de archivos
	print('Frecuencia : ',data_frecuencia)
    
def showFuzzy(): #difuso 1
	global normal
	spo2 = ctrl.Antecedent(np.arange(74, 100, 0.05), "oxygen_saturation")
	hr = ctrl.Antecedent(np.arange(45, 180, 0.05), "heart_rate")
	inestability = ctrl.Consequent(np.arange(0, 1, 0.001), "inestability")

	spo2["s1"] = fuzzy.trapmf(spo2.universe, [74, 74, 76, 82.5])
	spo2["s2"] = fuzzy.trapmf(spo2.universe, [74, 80, 85, 92])
	spo2["s3"] = fuzzy.trapmf(spo2.universe, [82.5, 90, 93.5, 97])
	spo2["s4"] = fuzzy.trapmf(spo2.universe, [92, 96, 100, 100])

	hr["h1"] = fuzzy.trapmf(hr.universe, [45, 45, 50, 70])
	hr["h2"] = fuzzy.trapmf(hr.universe, [45, 65, 80, 100])
	hr["h3"] = fuzzy.trimf(hr.universe, [70, 105, 130])
	hr["h4"] = fuzzy.trapmf(hr.universe, [100, 130, 180, 180])

	inestability["less_urgent"] = fuzzy.trapmf(inestability.universe, [0, 0, 0.04, 0.1])
	inestability["no_urgent"] = fuzzy.trapmf(inestability.universe, [0, 0.1, 0.35, 0.45])
	inestability["urgent"] = fuzzy.trapmf(inestability.universe, [0.35, 0.45, 0.75, 0.9])
	inestability["resuscitation"] = fuzzy.trapmf(inestability.universe, [0.75, 0.9, 1, 1])

	rule1 = ctrl.Rule(spo2["s1"] & hr["h1"], inestability["resuscitation"])
	rule2 = ctrl.Rule(spo2["s1"]& hr["h2"], inestability["urgent"])
	rule3 = ctrl.Rule(spo2["s1"] & hr["h3"], inestability["urgent"])
	rule4 = ctrl.Rule(spo2["s1"] & hr["h4"], inestability["resuscitation"])
	rule5 = ctrl.Rule(spo2["s2"] & hr["h1"], inestability["urgent"])
	rule6 = ctrl.Rule(spo2["s2"] & hr["h2"], inestability["urgent"])
	rule7 = ctrl.Rule(spo2["s2"] & hr["h3"], inestability["urgent"])
	rule8 = ctrl.Rule(spo2["s2"] & hr["h4"], inestability["urgent"])
	rule9 = ctrl.Rule(spo2["s3"] & hr["h1"], inestability["no_urgent"])
	rule10 = ctrl.Rule(spo2["s3"] & hr["h2"], inestability["no_urgent"])
	rule11 = ctrl.Rule(spo2["s3"] & hr["h3"], inestability["no_urgent"])
	rule12 = ctrl.Rule(spo2["s3"] & hr["h4"], inestability["urgent"])
	rule13 = ctrl.Rule(spo2["s4"] & hr["h1"], inestability["no_urgent"])
	rule14 = ctrl.Rule(spo2["s4"] & hr["h2"], inestability["less_urgent"])
	rule15 = ctrl.Rule(spo2["s4"] & hr["h3"], inestability["less_urgent"])
	rule16 = ctrl.Rule(spo2["s4"] & hr["h4"], inestability["no_urgent"])

	inestability_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16])
	measurement = ctrl.ControlSystemSimulation(inestability_ctrl)

	output = []
	#for i in range(len(data['SpO2(%)'])):
	#	measurement.input['oxygen_saturation'] = data['SpO2(%)'][i]
	#	measurement.input['heart_rate'] = data['PR(Bpm)'][i]
	#	measurement.compute()
	#	output.append(measurement.output['inestability'])
	measurement.input['oxygen_saturation'] = data_saturacion
	measurement.input['heart_rate'] = data_frecuencia
	measurement.compute()
	output.append(measurement.output['inestability'])
	
	normal = measurement.output['inestability']
	inestability.view(sim=measurement)
	#fig = plt.figure(1)
	#fig.canvas.set_window_title("Difuso normal")

	print("Grado de urgencia: ",measurement.output['inestability']) 
	if measurement.output['inestability'] >= 0 and measurement.output['inestability'] < 0.04:
		print("less_urgent - Codigo Verde, limite inferior")
	if measurement.output['inestability'] >= 0.04 and measurement.output['inestability'] < 0.1:
		print("less_urgent - Codigo Verde, limite superior")
	if measurement.output['inestability'] >= 0.1 and measurement.output['inestability'] < 0.35:
		print("no_urgent - Codigo Amarillo, limite inferior")
	if measurement.output['inestability'] >= 0.35 and measurement.output['inestability'] < 0.45:
		print("no_urgent - Codigo Amarillo, limite superior")
	if measurement.output['inestability'] >= 0.45 and measurement.output['inestability'] < 0.75:
		print("urgent - Codigo Naranja, limite inferior")
	if measurement.output['inestability'] >= 0.75 and measurement.output['inestability'] < 0.9:
		print("urgent - Codigo Naranja, limite superior")
	if measurement.output['inestability'] >= 0.9 and measurement.output['inestability'] <= 1:
		print("Resuscitacion - Codigo Rojo")
	#figura, axx = plt.subplots()
	#axx.plot(output)
	#plt.title('Probability of Failure', fontsize=13)
	#plt.xlabel('Time(seg)', fontsize=12)
	#plt.ylabel('Probability', fontsize=12)
	#plt.legend('P')
	#figura.canvas.set_window_title("Probabilidad de fallo normal")
	#plt.show()

def main():
	setValores(50,90)
	#getCSV()
	#plotCSV()
	showFuzzy()
	#movingMedianGraphSpO2()
	#movingMedianGraphHR()
	#movilFuzzy()

if __name__ == '__main__':
    app.run(debug=True)