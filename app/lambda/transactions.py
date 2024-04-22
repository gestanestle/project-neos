import os
import json
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
import random
import string
import uuid
import time
import simplejson as sjson

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ['TABLE_NAME'])
time = time.time()

def handler(event, context):
    statusCode = 200 
    headers = {
        "Content-Type": "application/json"
    }
    body = {}

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
                    item['amount'] = float(sjson.dumps(item['amount']))
                    body.append(item)

            elif  event['resource'] == '/api/transactions/{id}':
                id = event['pathParameters']['id']
                response = table.get_item(Key={'id':id})
                try:
                    item = response['Item']
                    item['amount'] = float(sjson.dumps(item['amount']))
                    body = item
                except KeyError:
                    body = "Transaction doesn't exist."


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
                
            body = { 'ref_id': ref_id }

        
    except Exception as e:  
        statusCode = 400
        body = str(e)

    res = {
        "statusCode": statusCode,
        "headers": headers,
        "body": json.dumps(body)
    }
    return res


def generate_ref_id():
  char_pool = string.ascii_letters + string.digits
  return ''.join(random.choices(char_pool, k=10))