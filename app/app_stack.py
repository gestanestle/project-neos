from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_source,
)
from constructs import Construct

from .construct_transaction import TransactionConstruct
from .construct_account import AccountConstruct

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        transactions = TransactionConstruct(self, 'TransactionsManager')
        accounts = AccountConstruct(self, 'AccountsManager')

        queue = sqs.Queue(
                    self, "AppQueue",
                    visibility_timeout=Duration.seconds(300),
                )
        sqs_event_source = lambda_event_source.SqsEventSource(queue)
        accounts.subscriber.add_event_source(sqs_event_source)

        api = apigw.RestApi(self, 'AppStackAPI')   
        api = api.root.add_resource('api')

        # Transaction Service
        t = api.add_resource('transactions')
        t_integ = apigw.LambdaIntegration(transactions.handler)

        t.add_method('POST', t_integ)
        t.add_method('GET', t_integ)
        tById = t.add_resource('{id}')
        tById.add_method('GET', t_integ)

        # Account Service
        a = api.add_resource('accounts')  
        a_integ = apigw.LambdaIntegration(accounts.handler)

        a.add_method('POST', a_integ)
        a.add_method('GET', a_integ)
        aById = a.add_resource('{id}')
        aById.add_method('GET', a_integ)
        aById.add_method('PUT', a_integ)
        aById.add_method('DELETE', a_integ)



        

    
        

        
