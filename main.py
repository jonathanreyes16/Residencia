#librerias
from flask import Flask, app
from flask.json import jsonify #, request, jsonify, flash, redirect,url_for
from flask.helpers import make_response
from flask_restful import Resource, Api, reqparse
from fuzzy import showFuzzy, getCSV #se importa la funcion fuzzy que se usara

import pandas as pd
import werkzeug


app = Flask(__name__)
api= Api(app)


parser = reqparse.RequestParser()
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')

#declaracion de las "funciones" de cada ruta
#lectura usando un valor
class Eval(Resource):
	def get(self, oxi,rc):
		r=showFuzzy(oxi,rc)
		return make_response(jsonify(
			{"data" : [{
				"Grado_de_urgencia" : r[0],
				"Triage": r[1],
				"Codigo": r[2],
				"Limite": r[3]
		}]
		}))
#lectura usando csv
class EvalCSV(Resource):
	def post(self):
		data = parser.parse_args()
		if data['file'] == "":
        		return {
                    'data':'',
                    'message':'No file found',
                    'status':'error'
                    }
		csv_data = pd.read_csv(data['file'])
		r=getCSV(csv_data)
		return make_response(jsonify(
			{"data" : [{
				"Grado_de_urgencia" : r[0],
				"Triage": r[1],
				"Codigo": r[2],
				"Limite": r[3]
		}]
		}))

#agrega las rutas
api.add_resource(Eval,'/eval/<float:oxi>_<float:rc>')
api.add_resource(EvalCSV,'/upload')


#if __name__ == '__main__':
#  app.run(host='localhost', debug=True, port=5000)