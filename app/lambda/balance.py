import os
import json
import boto3
from boto3.dynamodb.conditions import Key
import time
import simplejson as sjson

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ['TABLE_NAME'])
time = time.time()

def handler(event, context):
    return "from balance.py"