import os
import json
import boto3
from boto3.dynamodb.conditions import Key
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
        if event['resource'] == '/api/accounts':
            if event['httpMethod'] == 'GET':
                response = table.scan()

                items = response['Items']

                while 'LastEvaluatedKey' in response:
                    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response['Items'])

                body = []
                for item in items:
                    item['balance'] = float(sjson.dumps(item['balance']))
                    body.append(item)
            
            elif event['httpMethod'] == 'POST':
                requestJSON = json.loads(event['body'])

                first_name = requestJSON['first_name']
                last_name = requestJSON['last_name']
                email = requestJSON['email']

                id = str(uuid.uuid4())
                table.put_item(
                    Item={
                        'id': id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'balance': 0,
                        'timestamp': str(time)
                })

                body = { 'id': id }

        elif  event['resource'] == '/api/accounts/{id}':
            id = event['pathParameters']['id']

            if event['httpMethod'] == 'GET':
                response = table.get_item(Key={'id':id})
                item = response['Item']
                item['balance'] = float(sjson.dumps(item['balance']))
                body = item

            elif event['httpMethod'] == 'DELETE':
                table.delete_item(Key={'id':id})
                body = None

            elif event['httpMethod'] == 'PUT':
                requestJSON = json.loads(event['body'])

                first_name = requestJSON['first_name']
                last_name = requestJSON['last_name']
                email = requestJSON['email']
                
                item = table.update_item(
                    Key={'id':id},
                    UpdateExpression="set first_name = :f, last_name = :l, email = :e",
                    ExpressionAttributeValues={
                        ":f": first_name, 
                        ":l": last_name,
                        ":e": email
                    },
                    ReturnValues="UPDATED_NEW",
                )
                body = None
        
    except Exception as e:  
        statusCode = 400
        body = str(e)
    
    res = {
        "statusCode": statusCode,
        "headers": headers,
        "body": json.dumps(body)
    }
    return res