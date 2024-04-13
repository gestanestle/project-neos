import os
import json
import boto3
from decimal import Decimal
import random
import string
import uuid
import time

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ['HITS_TABLE_NAME'])


def lambda_handler(event, context):
    print(event)
    body = {}
    statusCode = 200
    headers = {
        "Content-Type": "application/json"
    }

    try:
        if event['routeKey'] == "GET /transactions?account={id}":
            items = table.get_item(
                Key={'accountId': event['queryStringParameters']['id']}
            )
            items = items["Items"]
            body = []
            for item in items:
                responseItems = [{
                     'id': item['id'], 
                     'accountId': item['accountId'],
                     'type': item['type'],
                     'amount': item['amount'],
                     'timestamp': item['timestamp']
                }]
                body.append(responseItems)

        elif event['routeKey'] == "GET /transactions/{id}":
            items = table.get_item(
                Key={'id': event['pathParameters']['id']}
            )
            item = items["Item"]
            body = [{
                    'id': item['id'], 
                    'accountId': item['accountId'],
                    'type': item['type'],
                    'amount': item['amount'],
                    'timestamp': item['timestamp']
            }]

        elif event['routeKey'] == "POST /transactions":
            requestJSON = json.loads(event['body'])

            ref_id = generate_ref_id
            source = requestJSON['source']
            destination = requestJSON['destination']
            type = requestJSON['type']
            amount = requestJSON['amount']
            time = time.time()

            if (type == 'CASH IN'):
                table.put_item(
                    Item={
                        'id': id = str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'accountId': destination,
                        'type': type,
                        'amount': amount,
                        'timestamp': time
                })

            elif (type == 'CASH OUT'):
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'accountId': source,
                        'type': type,
                        'amount': amount,
                        'timestamp': time
                })

            elif (type = 'FUND TRANSFER'):
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'accountId': source,
                        'type': { 'FUND TRANSFER': 'CASH OUT' },
                        'amount': amount,
                        'timestamp': time
                })
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'accountId': destination,
                        'type': { 'FUND TRANSFER': 'CASH IN' },
                        'amount': amount,
                        'timestamp': time
                })


            body = 'Create transaction with Reference ID: ' + ref_id
    except KeyError:
        statusCode = 400
        body = 'Unsupported route: ' + event['routeKey']
    body = json.dumps(body)
    res = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": body
    }
    return res


def generate_ref_id(length=10):
  char_pool = string.ascii_letters + string.digits
  return ''.join(random.choices(char_pool, k=length))
