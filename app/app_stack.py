from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

from .transaction_manager import TransactionManager

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        transactions = TransactionManager(self, 'TransactionsManager')

        api = apigw.RestApi(self, 'TransactionsAPI')   

        integration = apigw.LambdaIntegration(transactions.handler)

        apiV = api.root.add_resource('api')
        tranx = apiV.add_resource('transactions')
        tranx.add_method('POST', integration)
        tranx.add_method('GET', integration)
        tranxById = tranx.add_resource('{id}')
        tranxById.add_method('GET', integration)

    
        

        
