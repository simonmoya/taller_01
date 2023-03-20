from flask import render_template, url_for, flash, redirect,request, jsonify, make_response,Flask,session , Response, send_file
from flask_cors import CORS

import os
import pickle 
import json

from sklearn.ensemble import RandomForestClassifier
from flasgger import Swagger
from flasgger.utils import swag_from
from flasgger import LazyString, LazyJSONEncoder

app = Flask(__name__)
app.config['SECRET_KEY']="1234"
app.config["SWAGGER"] = {"title": "Swagger-UI", "uiversion": 2}

swagger_config = {
    "swagger_version": "2.0",
    "title": "API de predicción de pingüinos",
    "headers": [],
    "specs": [
        {
            "endpoint": "swagger_1",
            "route": "/swagger_1.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
    "description": "Esta es una API para predecir la especie de pingüino en base a sus características.",
}

CORS(app)
template = dict(
    swaggerUiPrefix=LazyString(lambda: request.environ.get("HTTP_X_SCRIPT_NAME", ""))
)

app.json_encoder = LazyJSONEncoder
swagger = Swagger(app, config=swagger_config, template=template)
   
@app.route("/inference", methods=['GET', 'POST'])
@swag_from('pinguino.yml')
def inference():
    """
    Predicción de la especie de pingüino en base a sus características
    ---
    parameters:
      - name: culmen_length_mm
        in: body
        type: number
        required: true
      - name: culmen_depth_mm
        in: body
        type: number
        required: true
      - name: flipper_length_mm
        in: body
        type: number
        required: true
      - name: body_mass_g
        in: body
        type: number
        required: true
    responses:
      200:
        description: Especie de pingüino predicha
        schema:
          properties:
            species:
              type: string
              description: Especie de pingüino predicha
    """
    print("Start Inference Process", str(request.method))
    if request.method != 'POST':
        return 'Only POST requests are allowed', 405
    
    filename = '/var/www/model/model_penguin.pk'
    model = pickle.load(open(filename, 'rb'))
    culmen_length_mm = request.json['culmen_length_mm']
    culmen_depth_mm = request.json['culmen_depth_mm']
    flipper_length_mm = request.json['flipper_length_mm']
    body_mass_g = request.json['body_mass_g']
    vector = [culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g]
    inference = model.predict([vector])
    class_penguin = ['Adelie','Chinstrap','Gentoo']
    result = {'species': class_penguin[int(inference)]}
    resp = make_response(result, 200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/swagger')
def apidocs():
    with open('pinguino.yml') as f:
        swag_data = yaml.load(f, Loader=yaml.FullLoader)
    ordered_properties = sorted(swag_data['parameters'][0]['schema']['properties'].items(), key=lambda x: x[1].get('order', 0))
    swag_data['parameters'][0]['schema']['properties'] = dict(ordered_properties)
    return jsonify(swag_data)
        
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)
