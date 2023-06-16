#!/usr/bin/env python3

import json
import uuid
import time
from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient, PartitionKey
from threading import Thread
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from flask import Flask, render_template
from flask import jsonify

def skalieren(array):
    mean = sum(array) / len(array)
    divided_array = [value / mean for value in array]
    return divided_array

def get_arrays():
   ENDPOINT = 'https://ampadb.documents.azure.com:443/'
   KEY = '61vexOJJciPItN1HC6CynbeSDT3dc2EhDVRMWo2ehQpTRZ1IVJNRuBbXyJNiGpC18iwy2K58bPgbACDb08Dr6w=='
   DATABASE_ID = 'cecdb'
   CONTAINER_ID = 'humidity'

   client = CosmosClient(url=ENDPOINT, credential=KEY)
   database = client.create_database_if_not_exists(id=DATABASE_ID)

   partition_key_path = PartitionKey(path="/deviceId")
   container = database.create_container_if_not_exists(
       id=CONTAINER_ID,
       partition_key=partition_key_path,
       offer_throughput=400,
   )

   curr_dt = datetime.now()
   timestamp = int(round(curr_dt.timestamp()))
   timestamp -= (36000 * 6) #6 Studen anzeigen

   query = f"SELECT * FROM c WHERE c._ts >= {timestamp}"
   array1 = []
   array2 = []
   array3 = []
   for doc in container.query_items(query, enable_cross_partition_query=True):
      array1.append(doc['humidity'])
      array2.append(datetime.fromtimestamp(doc['_ts']))
      array3.append(doc['voltage'])
   #array1 = np.array(result_array1)
   #array2 = np.array(result_array2)
   return array1, array2, array3

def update_graph():
    while True:
        humidity, timestamps, voltage = get_arrays()
        humidity = skalieren(humidity)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=voltage, name='voltage'))
        fig.add_trace(go.Scatter(x=timestamps, y=humidity, name='humidity'))
        fig.update_layout(title='Humidity + Voltage')
        graph_html = fig.to_html(full_html=False)
        with app.app_context():
            app.update_graph_data = graph_html
        print('updated')
        time.sleep(15)


app = Flask(__name__, template_folder='.')
@app.route("/")
def index():
    humidity, timestamps, voltage = get_arrays()
    humidity = skalieren(humidity)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=humidity, name='humidity'))
    fig.add_trace(go.Scatter(x=timestamps, y=voltage, name='voltage'))
    fig.update_layout(title='Humidity + Voltage')
    graph_html = fig.to_html(full_html=False)
 
    return render_template("index.html", graph=graph_html) 

if __name__=='__main__':
    update_thread = Thread(target=update_graph)
    update_thread.start()
    app.run(debug=True, threaded=True)
