from flask import render_template, url_for, flash, redirect,request, jsonify, make_response,Flask,session , Response, send_file
from flask_cors import CORS

import pandas as pd
import os
import json

from sqlalchemy import create_engine
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer


app = Flask(__name__)
app.config['SECRET_KEY']="1234"
CORS(app)

def Connect_Pg():
    with open('config_jav.json') as config_file:
        data = json.load(config_file)

    engine = create_engine('postgresql://'+data['pgsql']['user']+':'+data['pgsql']['passwd']+
          "@"+data['pgsql']['host']+":"+data['pgsql']['port']+"/"+data['pgsql']['db'])
    
    return engine

def execute_query(query, engine):
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()
    conn.close()
    
#Genera la lista de registros de cada tabla de acuerdo a la tabla config_table                                
@app.route("/load", methods=['POST'])
def LoadData():
    for tablename in tables:
        file = './'+tablename+'.csv'
        df = pd.read_csv(str(file), lineterminator='\n')    
        engine = Connect_Pg()
        df.to_sql(tablename, engine, if_exists='append', index=False)
    print("Success Load Tables")

@app.route("/delete", methods=['POST'])
def DropData():
    engine = Connect_Pg()
    for tablename in tables:
        query = 'Truncate '+tablename
        execute_query(query, engine)
    print("Success Truncate Tables")

@app.route("/train", methods=['POST'])
def ModelTrain():
    engine = Connect_Pg()
    conn_pgsql = engine.connect()
    Sql = "Select * from penguins_size"
    df_penguin = pd.read_sql_query(Sql, conn_pgsql)
    imputer = SimpleImputer(strategy='most_frequent')
    df_penguin.iloc[:,:] = imputer.fit_transform(df_penguin)
    features = ['culmen_length_mm', 'culmen_depth_mm'] 
    X = df_penguin[['culmen_length_mm','culmen_depth_mm','flipper_length_mm','body_mass_g']]
    y = df_penguin['species']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=101)
    forest = RandomForestClassifier(criterion='entropy', n_estimators=100, max_depth=None)
    forest.fit(X_train, y_train) 
    forest_preds = forest.predict(X_test) 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
