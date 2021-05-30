from flask import Flask, request, jsonify
import boto3
import os
import logging
import json
from flask.templating import render_template
import decimal


logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = 'us-east-1'
MODE_DEBUG = False
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


app = Flask(__name__, template_folder="html", static_folder="html/static")
app.json_encoder = DecimalEncoder

MODE = "LOCAL"


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/api/options', methods=['GET', 'OPTIONS'])
def get_options():
    data = []
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
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
    return jsonify(data)


@app.route('/api/options', methods=['POST'])
def vote_option():
    content = request.json
    logging.info("Returning options")
    logging.info("Request received: {}".format(content))

    response = {}
    if "ID" not in content:
        response['message'] = "Malformed request"
        return jsonify(response), 400

    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(os.getenv("TABLE_NAME"))
    table.update_item(
        Key={
            'ID': content['ID'],
        },
        UpdateExpression='ADD votes :inc',
        ExpressionAttributeValues={
            ':inc': 1
        }
    )
    response['message'] = "Request processed"
    return jsonify(response), 200


if __name__ == '__main__':
    MODE = os.environ['MODE'] if "MODE" in os.environ else "LOCAL"
    if MODE == "LOCAL":
        os.environ['TABLE_NAME'] = "apprunner-demo-data"
        MODE_DEBUG = True
    app.run(port=8080, host="0.0.0.0", debug=MODE_DEBUG)
