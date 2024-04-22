from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb
)

class AccountConstruct(Construct):

    @property
    def handler(self):
        return self._handler  
    
    
    @property
    def subscriber(self):
        return self._subscriber


    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        table = ddb.Table(
            self, 'Account',
            partition_key={'name': 'id', 'type': ddb.AttributeType.STRING},
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=20,
            write_capacity=20,
            # sort_key={'name': 'timestamp', 'type': ddb.AttributeType.STRING},
        )

        self._handler = _lambda.Function(
            self, 'AccountsHandler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='accounts.handler',
            code=_lambda.Code.from_asset('app/lambda'),
            environment={
                'TABLE_NAME': table.table_name,
            }
        )

        self._subscriber = _lambda.Function(
            self, 'BalanceHandler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='balance.handler',
            code=_lambda.Code.from_asset('app/lambda'),
            environment={
                'TABLE_NAME': table.table_name,
            }
        )

        table.grant_read_write_data(self._handler)
        table.grant_read_write_data(self._subscriber)

