from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_integrations
)
import aws_cdk as core
from constructs import Construct

class ExampleHttpApiLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM Role for Lambda execution
        lambda_role = iam.Role(
            self, "ExampleLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "LambdaExecutionPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                              "logs:CreateLogGroup"
                            ],
                            resources=[
                              f"arn:aws:logs:us-east-1:{self.account}:*"
                            ]
                        ),
                        iam.PolicyStatement(
                            actions=[
                              "logs:CreateLogStream", 
                              "logs:PutLogEvents"
                            ],
                            resources=[
                              f"arn:aws:logs:us-east-1:{self.account}:log-group:/aws/lambda/example-lambda:*"
                            ]
                        )
                    ]
                )
            }
        )

        # Add the AWS Lambda Powertools layer
        powertools_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            id="LambdaPowertoolsLayer",
            layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:73"
        )

        # Create the Lambda function
        example_lambda = _lambda.Function(
            self, "ExampleLambdaFunction",
            function_name="example-lambda",
            description="Example Lambda Descriotion",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[powertools_layer],
            environment={
                "EXAMPLE_ENV": "EXAMPLE_ENV_VALUE"
            },
            timeout=core.Duration.minutes(5),
            role=lambda_role
        )

        # Create HTTP API Gateway for the Lambda function
        api = apigwv2.HttpApi(
            self, "ExampleHttpApi",
            api_name="example-http-api",
            create_default_stage=True
        )

        # Create the Lambda Integration
        lambda_integration = apigwv2_integrations.HttpLambdaIntegration(
            id="ExampleLambdaIntegration",
            handler=example_lambda
        )

        # Create the route in the HTTP API Gateway
        api.add_routes(
            path="/example-endpoint",
            methods=[apigwv2.HttpMethod.POST],
            integration=lambda_integration
        )
