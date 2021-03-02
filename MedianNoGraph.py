from flask import Flask, app, request
from flask_restful import Resource, Api

from skfuzzy import control as ctrl
from sklearn.metrics import mean_absolute_error
import pandas as pd
import numpy as np
import skfuzzy as fuzzy

app = Flask(__name__)
api= Api(app)

#ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

#@app.route('/upload/', methods=['GET', 'POST'])
#def upload():
#	if request.method == 'POST':
#		file = request.files['file']
#		if file:
#			filename = secure_filename(file.filename)
#			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#			a = 'file uploaded'
#	return render_template('upload.html', data = a)


#ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
#
#class UploadCSV(Resource):
#
#    def post(self):
#        files = request.files['file']
#        files.save(os.path.join(ROOT_PATH,files.filename))
#        data = pd.read_csv(os.path.join(ROOT_PATH,files.filename))
#        print(data)
#
#api.add_resource(UploadCSV, '/v1/upload')

class UploadCSV(Resource):
	def post(self):
		file = request.files['file']
		data = pd.read_csv(file)
		print(data)


api.add_resource(UploadCSV,'/upload')

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
	for i in range(len(data['SpO2(%)'])):
		measurement.input['oxygen_saturation'] = data['SpO2(%)'][i]
		measurement.input['heart_rate'] = data['PR(Bpm)'][i]
		measurement.compute()
		output.append(measurement.output['inestability'])

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


def movingMedianGraphSpO2(): #optimizacion
	global df3
	data_saturacion_fuzzy = data_saturacion
	data_saturacion_fuzzy_media = data_saturacion_fuzzy.median()
	df3 = data_saturacion_fuzzy.rolling(window=15).median()

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
	df4 = data_frecuencia_fuzzy.rolling(window=15).median()

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


def main():
	getCSV()
	#plotCSV()
	showFuzzy()
	movingMedianGraphSpO2()
	movingMedianGraphHR()
	movilFuzzy()


if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)