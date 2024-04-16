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
        api.root.add_method('GET', integration)
        api.root.add_method('POST', integration)

    
        

        
