from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb
)

class TransactionConstruct(Construct):

    @property
    def handler(self):
        return self._handler  


    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        table = ddb.Table(
            self, 'Transaction',
            partition_key={'name': 'id', 'type': ddb.AttributeType.STRING},
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=20,
            write_capacity=20,
            # sort_key={'name': 'timestamp', 'type': ddb.AttributeType.STRING},
        )

        self._handler = _lambda.Function(
            self, 'TransactionsHandler',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='transactions.handler',
            code=_lambda.Code.from_asset('app/lambda'),
            environment={
                'TABLE_NAME': table.table_name,
            }
        )

        table.grant_read_write_data(self._handler)

