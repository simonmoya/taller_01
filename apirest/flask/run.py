from flask import render_template, url_for, flash, redirect,request, jsonify, make_response,Flask,session , Response, send_file
from flask_cors import CORS

import pandas as pd
import os
import json
import pickle 

from sqlalchemy import create_engine
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer


app = Flask(__name__)
app.config['SECRET_KEY']="1234"
CORS(app)

def Connect_Pg():
    host = os.environ.get('DB_HOST')
    user = os.environ.get('DB_USER')
    passwd = os.environ.get('DB_PASSWORD')
    port = os.environ.get('DB_PORT')
    db = os.environ.get('DB_NAME')
    print('DataBase: ',db)

    engine = create_engine('postgresql://'+user+':'+passwd+"@"+host+":"+port+"/"+db)
    
    return engine

def execute_query(query, engine):
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()
    conn.close()
    
#Genera la lista de registros de cada tabla de acuerdo a la tabla config_table                                
@app.route("/load", methods=['GET', 'POST'])
def LoadData():
    url="https://raw.githubusercontent.com/tensorflow/tfx/master/tfx/examples/penguin/data/labelled/penguins_processed.csv"
    df = pd.read_csv(url, lineterminator='\n')    
    engine = Connect_Pg()
    tablename = 'penguins_size'
    df.to_sql(tablename, engine, if_exists='append', index=False)
    print("Success Load Tables")
    resp=make_response("Success Load Tables")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp    

@app.route("/delete", methods=['GET', 'POST'])
def DeleteData():
    engine = Connect_Pg()
    query = 'Truncate penguins_size'
    execute_query(query, engine)
    print("Success Truncate Tables")
    resp=make_response("Success Truncate Tables")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp    

@app.route("/modeltrain", methods=['GET', 'POST'])
def ModelTrain():
    engine = Connect_Pg()
    conn_pgsql = engine.connect()
    Sql = "Select * from penguins_size"
    df_penguin = pd.read_sql_query(Sql, conn_pgsql)
    if (len(df_penguin) > 0):
        conn_pgsql.close()
        imputer = SimpleImputer(strategy='most_frequent')
        df_penguin.iloc[:,:] = imputer.fit_transform(df_penguin)
        features = ['culmen_length_mm', 'culmen_depth_mm'] 
        X = df_penguin[['culmen_length_mm','culmen_depth_mm','flipper_length_mm','body_mass_g']].to_numpy()
        y = df_penguin['species'].to_numpy()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=101)
        model = RandomForestClassifier(criterion='entropy', n_estimators=100, max_depth=None)
        model.fit(X_train, y_train) 
        forest_preds = model.predict(X_test)
        report = classification_report(y_test, forest_preds, output_dict=True)
        df = pd.DataFrame(report).transpose()
        filename = '/var/www/model/model_penguin.pk'
        pickle.dump(model, open(filename, 'wb'))
        print('Success Trainning Model')
        resp=make_response("Success Trainning Model")
        #return df, X_test, y_test
    else:
        print('No data Found!')
        resp=make_response("No data Found!")        
        #return None, None, None
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
