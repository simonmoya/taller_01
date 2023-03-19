from flask import render_template, url_for, flash, redirect,request, jsonify, make_response,Flask,session , Response, send_file
from flask_cors import CORS

import os
import pickle 
import json

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from flasgger import Swagger
from flasgger.utils import swag_from
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

app = Flask(__name__)
app.config['SECRET_KEY']="1234"
CORS(app)
swagger = Swagger(app)
   
@app.route("/inference", methods=['GET', 'POST'])
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
    
    filename = 'model_penguin.pk'
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
        
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
