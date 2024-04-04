from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)
from constructs import Construct

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "AppQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        hello = _lambda.Function(self, 'helloFunc',
            runtime=_lambda.Runtime.PYTHON_3_11,  
            handler='hello.handler',
            code=_lambda.Code.from_asset('app/lambda/')
        )

        # api = apigw.RestApi(self, "HelloFuncAPI")
        # integration = apigw.LambdaIntegration(hello)
        # api.root.add_method("GET", integration)

        api = apigw.LambdaRestApi(self, "HelloFuncAPI", handler=hello)

        items = api.root.add_resource("greetings")
        items.add_method("GET") # GET /items

        
