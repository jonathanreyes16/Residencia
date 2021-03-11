#from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk 
#from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
#from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from skfuzzy import control as ctrl
from sklearn.metrics import mean_absolute_error
#from time import process_time
#from timeit import default_timer as timer
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import skfuzzy as fuzzy

def getCSV ():
    global df
    global data
    global import_file_path
    global data_frecuencia
    global data_saturacion

    df = pd.read_csv ("C:\\Users\\Jona_\\Documents\\RESIDENCIA\\cv2000\\codVerde1-2k.csv")
    data = df.drop(["Unnamed: 0"],axis=1)
    data.rename(columns={"SpO2":"SpO2(%)","HR":"PR(Bpm)"}, inplace=True)
    data_saturacion = data['SpO2(%)']
    data_frecuencia = data['PR(Bpm)']
    print("----------------------------------------------------------------------------------------------------")
    print('Saturacion promedio: ',data_saturacion.mean()) #promedios de archivos
    print('Frecuencia promedio: ',data_frecuencia.mean())

# def plotCSV ():
# 	global my_progress

# 	df2 = data[['SpO2(%)', 'PR(Bpm)']]
# 	fig, axes = plt.subplots(nrows=2, ncols=1)
# 	df2.plot(ax=axes[0], title = 'Raw values',kind='line', y='PR(Bpm)',ylabel = 'PR(Bpm)')
# 	df2.plot(ax=axes[1] ,y='SpO2(%)', xlabel = 'Time(seg)', ylabel = 'SpO2(%)')

#-----------------------------------Subir archivo-----------------------------------------------
def getCSV (datas):
    df = datas
    data = df.drop(["Unnamed: 0"],axis=1)
    data.rename(columns={"SpO2":"SpO2(%)","HR":"PR(Bpm)"}, inplace=True)
    data_saturacion = data['SpO2(%)']
    data_frecuencia = data['PR(Bpm)']
    print("----------------------------------------------------------------------------------------------------")
    print('Saturacion promedio: ',data_saturacion.mean())
    print('Frecuencia promedio: ',data_frecuencia.mean())
    return showFuzzy1(data_saturacion,data_frecuencia)
#-----------------------------------Subir archivo-----------------------------------------------



def showFuzzy1(sat,freq): #difuso 1
	#global normal
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

	#output = []
	#for i in range(len(data['SpO2(%)'])):
	#	measurement.input['oxygen_saturation'] = data['SpO2(%)'][i]
	#	measurement.input['heart_rate'] = data['PR(Bpm)'][i]
	#	measurement.compute()
	#	output.append(measurement.output['inestability'])

	output = []
	for i in range(len(sat)):
		measurement.input['oxygen_saturation'] = sat[i]
		measurement.input['heart_rate'] = freq[i]
		measurement.compute()
		output.append(measurement.output['inestability'])
	#normal = measurement.output['inestability']
	#inestability.view(sim=measurement)
	#fig = plt.figure(1)
	#fig.canvas.set_window_title("Difuso normal")

	grado_urgencia=measurement.output['inestability']
	if measurement.output['inestability'] >= 0 and measurement.output['inestability'] < 0.04:
		triage, codigo, limite = "less_urgent" , "Verde" , "inferior"
	if measurement.output['inestability'] >= 0.04 and measurement.output['inestability'] < 0.1:
		triage, codigo, limite = "less_urgent" , "Verde" , "superior"
	if measurement.output['inestability'] >= 0.1 and measurement.output['inestability'] < 0.35:
		triage, codigo, limite = "no_urgent" , "amarillo" , "inferior"
	if measurement.output['inestability'] >= 0.35 and measurement.output['inestability'] < 0.45:
		triage, codigo, limite = "no_urgent" , "amarillo" , "superior"
	if measurement.output['inestability'] >= 0.45 and measurement.output['inestability'] < 0.75:
		triage, codigo, limite = "urgent" , "naranja" , "inferior"
	if measurement.output['inestability'] >= 0.75 and measurement.output['inestability'] < 0.9:
		triage, codigo, limite = "urgent" , "naranja" , "inferior"
	if measurement.output['inestability'] >= 0.9 and measurement.output['inestability'] <= 1:
		triage, codigo, limite = "resuscitacion" , "rojo" , "superior"
	return grado_urgencia,triage,codigo,limite

	#print("Grado de urgencia: ",measurement.output['inestability'])
	#if measurement.output['inestability'] >= 0 and measurement.output['inestability'] < 0.04:
	#	print("less_urgent - Codigo Verde, limite inferior")
	#if measurement.output['inestability'] >= 0.04 and measurement.output['inestability'] < 0.1:
	#	print("less_urgent - Codigo Verde, limite superior")
	#if measurement.output['inestability'] >= 0.1 and measurement.output['inestability'] < 0.35:
	#	print("no_urgent - Codigo Amarillo, limite inferior")
	#if measurement.output['inestability'] >= 0.35 and measurement.output['inestability'] < 0.45:
	#	print("no_urgent - Codigo Amarillo, limite superior")
	#if measurement.output['inestability'] >= 0.45 and measurement.output['inestability'] < 0.75:
	#	print("urgent - Codigo Naranja, limite inferior")
	#if measurement.output['inestability'] >= 0.75 and measurement.output['inestability'] < 0.9:
	#	print("urgent - Codigo Naranja, limite superior")
	#if measurement.output['inestability'] >= 0.9 and measurement.output['inestability'] <= 1:
	#	print("Resuscitacion - Codigo Rojo")

	#figura, axx = plt.subplots()
	#axx.plot(output)
	#plt.title('Probability of Failure', fontsize=13)
	#plt.xlabel('Time(seg)', fontsize=12)
	#plt.ylabel('Probability', fontsize=12)
	#plt.legend('P')
	#figura.canvas.set_window_title("Probabilidad de fallo normal")
	#plt.show()



#--------------------------------------#difuso 1 modificado------------------------------------------
def showFuzzy(saturacion,frecuencia):

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

	#output = []
	#for i in range(len(data['SpO2(%)'])):
	#	measurement.input['oxygen_saturation'] = data['SpO2(%)'][i]
	#	measurement.input['heart_rate'] = data['PR(Bpm)'][i]
	#	measurement.compute()
	#	output.append(measurement.output['inestability'])

	output = []
	measurement.input['oxygen_saturation'] = saturacion
	measurement.input['heart_rate'] = frecuencia
	measurement.compute()
	output.append(measurement.output['inestability'])

	#normal = measurement.output['inestability']
	#inestability.view(sim=measurement)
	#fig = plt.figure(1)
	#fig.canvas.set_window_title("Difuso normal")

	#print("Grado de urgencia: ",measurement.output['inestability'])
	#if measurement.output['inestability'] >= 0 and measurement.output['inestability'] < 0.04:
	#	print("less_urgent - Codigo Verde, limite inferior")
	#if measurement.output['inestability'] >= 0.04 and measurement.output['inestability'] < 0.1:
	#	print("less_urgent - Codigo Verde, limite superior")
	#if measurement.output['inestability'] >= 0.1 and measurement.output['inestability'] < 0.35:
	#	print("no_urgent - Codigo Amarillo, limite inferior")
	#if measurement.output['inestability'] >= 0.35 and measurement.output['inestability'] < 0.45:
	#	print("no_urgent - Codigo Amarillo, limite superior")
	#if measurement.output['inestability'] >= 0.45 and measurement.output['inestability'] < 0.75:
	#	print("urgent - Codigo Naranja, limite inferior")
	#if measurement.output['inestability'] >= 0.75 and measurement.output['inestability'] < 0.9:
	#	print("urgent - Codigo Naranja, limite superior")
	#if measurement.output['inestability'] >= 0.9 and measurement.output['inestability'] <= 1:
	#	print("Resuscitacion - Codigo Rojo")

	grado_urgencia=measurement.output['inestability']
	if measurement.output['inestability'] >= 0 and measurement.output['inestability'] < 0.04:
		triage, codigo, limite = "less_urgent" , "Verde" , "inferior"
	if measurement.output['inestability'] >= 0.04 and measurement.output['inestability'] < 0.1:
		triage, codigo, limite = "less_urgent" , "Verde" , "superior"
	if measurement.output['inestability'] >= 0.1 and measurement.output['inestability'] < 0.35:
		triage, codigo, limite = "no_urgent" , "amarillo" , "inferior"
	if measurement.output['inestability'] >= 0.35 and measurement.output['inestability'] < 0.45:
		triage, codigo, limite = "no_urgent" , "amarillo" , "superior"
	if measurement.output['inestability'] >= 0.45 and measurement.output['inestability'] < 0.75:
		triage, codigo, limite = "urgent" , "naranja" , "inferior"
	if measurement.output['inestability'] >= 0.75 and measurement.output['inestability'] < 0.9:
		triage, codigo, limite = "urgent" , "naranja" , "inferior"
	if measurement.output['inestability'] >= 0.9 and measurement.output['inestability'] <= 1:
		triage, codigo, limite = "resuscitacion" , "rojo" , "superior"
	return grado_urgencia,triage,codigo,limite

	#figura, axx = plt.subplots()
	#axx.plot(output)
	#plt.title('Probability of Failure', fontsize=13)
	#plt.xlabel('Time(seg)', fontsize=12)
	#plt.ylabel('Probability', fontsize=12)
	#plt.legend('P')
	#figura.canvas.set_window_title("Probabilidad de fallo normal")
	#plt.show()

#--------------------------------------#difuso 1 modificado------------------------------------------

def movingMedianGraphSpO2(): #optimizacion
	global df3
	data_saturacion_fuzzy = data_saturacion
	data_saturacion_fuzzy_media = data_saturacion_fuzzy.median()
#	data_saturacion_fuzzy.plot(color='#024A86', linewidth=3, figsize=(10,6))
	df3 = data_saturacion_fuzzy.rolling(window=15).median()
#	plt.plot(df3,color='magenta')
#   modify ticks size
#	plt.xticks(fontsize=14)
#	plt.yticks(fontsize=14)
#	plt.legend(fontsize=14)
# title and labels
#	plt.title('Movil Median - Oxygen Saturation', fontsize=16)
#	plt.xlabel('Time(seg)', fontsize=14)
#	plt.ylabel('SpO2', fontsize=14)
#	fig = plt.figure(1)
#	fig.canvas.set_window_title("Metodo Mediana SpO2")
#	plt.show()

# mean absolute error
	y_true = data_saturacion_fuzzy
	y_pred = df3
	y_true.to_numpy()
	y_pred.to_numpy()
	print("Error absoluto SpO2: ",mean_absolute_error(y_true[15:], y_pred[15:]))


def movingMedianGraphHR(): #optimizacion
	global df4
	data_frecuencia_fuzzy = data_frecuencia
	data_frecuencia_fuzzy_media = data_frecuencia_fuzzy.median()
	#data_frecuencia_fuzzy.plot(color='#024A86', linewidth=3, figsize=(10,6))
	df4 = data_frecuencia_fuzzy.rolling(window=15).median()
	#plt.plot(df4,color='magenta')

# modify ticks size
	#plt.xticks(fontsize=14)
	#plt.yticks(fontsize=14)
	#plt.legend(fontsize=14)
# title and labels
	#plt.title('Movil Median - Heart rate', fontsize=16)
	#plt.xlabel('Time(seg)', fontsize=14)
	#plt.ylabel('PR(Bpm)', fontsize=14)
	#fig = plt.figure(1)
	#fig.canvas.set_window_title("Metodo Mediana HR")
	#plt.show()

	# mean absolute error
	y_true = data_frecuencia_fuzzy
	y_pred = df4
	y_true.to_numpy()
	y_pred.to_numpy()
	print("Error absoluto HR: ",mean_absolute_error(y_true[15:], y_pred[15:]))


def movilFuzzy(): #difuso 2
	global movil
	both = pd.concat([df3,df4],axis=1)

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
	for i in range(len(both['SpO2(%)'])):
		measurement.input['oxygen_saturation'] = both['SpO2(%)'][i]
		measurement.input['heart_rate'] = both['PR(Bpm)'][i]
		measurement.compute()
		output.append(measurement.output['inestability'])

	movil = measurement.output['inestability']
	print(">>>>>>>>>>>>>>>>>>>>>>Difuso con Mediana Movil<<<<<<<<<<<<<<<<<<<<<<<<<<")

	#inestability.view(sim=measurement)
	#fig = plt.figure(1)
	#fig.canvas.set_window_title("Difuso mediana")

	print("Grado de urgencia movilFuzzy: ",measurement.output['inestability'])
	if measurement.output['inestability'] >= 0 and measurement.output['inestability'] < 0.04:
		print("less_urgent movilFuzzy - Codigo Verde, limite inferior")
	if measurement.output['inestability'] >= 0.04 and measurement.output['inestability'] < 0.1:
		print("less_urgent movilFuzzy - Codigo Verde, limite superior")
	if measurement.output['inestability'] >= 0.1 and measurement.output['inestability'] < 0.35:
		print("no_urgent movilFuzzy - Codigo Amarillo, limite inferior")
	if measurement.output['inestability'] >= 0.35 and measurement.output['inestability'] < 0.45:
		print("no_urgent movilFuzzy - Codigo Amarillo, limite superior")
	if measurement.output['inestability'] >= 0.45 and measurement.output['inestability'] < 0.75:
		print("urgent movilFuzzy - Codigo Naranja, limite inferior")
	if measurement.output['inestability'] >= 0.75 and measurement.output['inestability'] < 0.9:
		print("urgent movilFuzzy - Codigo Naranja, limite superior")
	if measurement.output['inestability'] >= 0.9 and measurement.output['inestability'] < 1:
		print("Resuscitacion movilFuzzy - Codigo Rojo")
#	figura, axx = plt.subplots()
#	axx.plot(output)
#	plt.title('Probability of Failure', fontsize=13)
#	plt.xlabel('Time(seg)', fontsize=12)
#	plt.ylabel('Probability', fontsize=12)
#	plt.legend('P')
#	figura.canvas.set_window_title("Probabilidad de fallo con difuso mediana")
#	plt.show()


def main():
	getCSV()
	#plotCSV()
	showFuzzy()
	movingMedianGraphSpO2()
	movingMedianGraphHR()
	movilFuzzy()



if __name__ == "__main__":

    main()