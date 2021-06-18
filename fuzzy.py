
from skfuzzy import control as ctrl
from sklearn.metrics import mean_absolute_error
import pandas as pd
import numpy as np
import skfuzzy as fuzzy


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

	output = []
	for i in range(len(sat)):
		measurement.input['oxygen_saturation'] = sat[i]
		measurement.input['heart_rate'] = freq[i]
		measurement.compute()
		output.append(measurement.output['inestability'])


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

	output = []
	measurement.input['oxygen_saturation'] = saturacion
	measurement.input['heart_rate'] = frecuencia
	measurement.compute()
	output.append(measurement.output['inestability'])


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

#--------------------------------------#difuso 1 modificado------------------------------------------