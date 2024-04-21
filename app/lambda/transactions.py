import os
import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
import random
import string
import uuid
import time

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ['TABLE_NAME'])
time = time.time()

def handler(event, context):
    print(event)
    body = {}
    statusCode = 200
    headers = {
        "Content-Type": "application/json"
    }

    try:
        if event['httpMethod'] == 'GET':
            if event['queryStringParameters'] is not None:
                accId = event['queryStringParameters']['account_id']

                response = table.scan(FilterExpression = Attr('account_id').eq(accId))
                items = response['Items']

                while 'LastEvaluatedKey' in response:
                    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response['Items'])

                body = []
                for item in items:
                    body.append(item)

                body = str(body)

            elif  event['resource'] == '/api/transactions/{id}':
                id = event['pathParameters']['id']
                response = table.get_item(
                    Key={'id':id}
                )
                item = response['Item']
                body = str(item)

        elif event['httpMethod'] == 'POST':
            requestJSON = json.loads(event['body'])

            ref_id = generate_ref_id()
            source = requestJSON['source']
            destination = requestJSON['destination']
            type = requestJSON['type']
            amount = requestJSON['amount']

            if (type == 'CASH IN'):
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'account_id': destination,
                        'type': type,
                        'amount': amount,
                        'timestamp': str(time)
                })

            elif (type == 'CASH OUT'):
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'account_id': source,
                        'type': type,
                        'amount': amount,
                        'timestamp': str(time)
                })

            elif (type == 'FUND TRANSFER'):
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'account_id': source,
                        'type': { 'FUND TRANSFER': 'CASH OUT' },
                        'amount': amount,
                        'timestamp': str(time)
                })
                table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'ref_id': ref_id,
                        'account_id': destination,
                        'type': { 'FUND TRANSFER': 'CASH IN' },
                        'amount': amount,
                        'timestamp': str(time)
                })
                
            body = 'Create transaction with Reference ID: ' + ref_id
        
    except Exception as e:  
        statusCode = 400
        body = str(e)

    res = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
        }
    return res


def generate_ref_id():
  char_pool = string.ascii_letters + string.digits
  return ''.join(random.choices(char_pool, k=10))