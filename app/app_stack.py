from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)
from constructs import Construct

from .hitcounter import HitCounter
from .transaction_manager import TransactionManager

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # hello = _lambda.Function(
        #     self, 'HelloHandler',
        #     runtime=_lambda.Runtime.PYTHON_3_11,  
        #     code=_lambda.Code.from_asset('app/lambda'),
        #     handler='hello.handler'
        # )

        # api = apigw.LambdaRestApi(self, "HelloFuncAPI", handler=hello)

        # items = api.root.add_resource("greetings")
        # items.add_method("GET") # GET /items

        # hello_with_counter = HitCounter(
        #     self, 'HelloHitCounter',
        #     downstream=hello,
        # )

        # apigw.LambdaRestApi(
        #     self, 'HCEndpoint',
        #     handler=hello_with_counter.handler,
        # )

        transactions = TransactionManager(self, 'TransactionsManager')

        apigw.LambdaRestApi(
            self, 'TransactionsAPI',
            handler=transactions.handler,
        )
        

        
