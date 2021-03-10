from flask import Flask, app, request, jsonify
from flask.helpers import make_response
from flask_restful import Resource, Api
from fuzzy import showFuzzy

app = Flask(__name__)
api= Api(app)

#@app.route('/eval/<oxi>_<rc>')
#def evaluacion(oxi,rc):
#	return jsonify(showFuzzy(oxi,rc))

class Eval(Resource):
	def get(self, oxi,rc):
		#return jsonify(oxi,rc)
		r=showFuzzy(oxi,rc)
		return make_response(
			{"data" : [{
				"Grado_de_urgencia" : r[0],
				"Triage": r[1],
				"Codigo": r[2],
				"Limite": r[3]
		}]
		})

api.add_resource(Eval,'/eval/<float:oxi>_<float:rc>')

if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=5000)