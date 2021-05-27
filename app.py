from flask import Flask
import boto3 
import os
from flask import jsonify


app = Flask(__name__)

@app.route('/')
def hello_world():
   return("Hello World!")

@app.route('/api/options')
def get_options():
   data = []
   dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
   table = dynamodb.Table(os.getenv("TABLE_NAME"))
   scan_kwargs = {}
   done = False
   start_key = None
   while not done:
      if start_key:
         scan_kwargs['ExclusiveStartKey'] = start_key
      response = table.scan(**scan_kwargs)
      data.extend(response.get('Items'))
      start_key = response.get('LastEvaluatedKey', None)
      done = start_key is None
   return jsonify.dumps(data)

if __name__ == '__main__':
   app.run(port=8080, host="0.0.0.0")