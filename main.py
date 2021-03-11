from ast import parse
from flask import Flask, app, request
from flask.json import jsonify #, request, jsonify, flash, redirect,url_for
import werkzeug, os
from flask.helpers import make_response
from flask_restful import Resource, Api, reqparse
from fuzzy import showFuzzy, getCSV #se importa la funcion fuzzy que se usara
import pandas as pd

from werkzeug.utils import secure_filename

app = Flask(__name__)
api= Api(app)

parser = reqparse.RequestParser()
parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')

UPLOAD_FOLDER = 'uploads/'
#define el tamano maximo de los archivos a subir 16mb
#y la extension del archivo
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#declaracion de las "funciones" de cada ruta
#lectura usando un valor
class Eval(Resource):
	def get(self, oxi,rc):
		r=showFuzzy(oxi,rc)
		return make_response(
			{"data" : [{
				"Grado_de_urgencia" : r[0],
				"Triage": r[1],
				"Codigo": r[2],
				"Limite": r[3]
		}]
		})
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
		return make_response(
			{"data" : [{
				"Grado_de_urgencia" : r[0],
				"Triage": r[1],
				"Codigo": r[2],
				"Limite": r[3]
		}]
		})

class ex(Resource):#ejemplo de subida de archivo
	def post(self):
		if 'file' not in request.files:
			resp = jsonify ({'message': 'no file part in the request'})
			resp.status_code=400
			return resp
		file= request.files['file']
		if file.filename == '':
			resp = jsonify({'message' : 'No file selected for uploading'})
			resp.status_code = 400
			return resp
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			resp = jsonify({'message' : 'File successfully uploaded'})
			resp.status_code = 201
			return resp
		else:
			resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
			resp.status_code = 400
			return resp

#agrega las rutas
api.add_resource(Eval,'/eval/<float:oxi>_<float:rc>')
api.add_resource(EvalCSV,'/upload')
api.add_resource(ex,'/upload2')


#if __name__ == '__main__':
#  app.run(host='localhost', debug=True, port=5000)