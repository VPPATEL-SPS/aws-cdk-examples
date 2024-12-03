from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigw
)
import aws_cdk as core
from constructs import Construct

class ExampleRestApiLambdaStack(Stack):
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

        # Add the AWS Lambda Powertools layer (Optional)
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

        # Create Rest API
        example_api = apigw.LambdaRestApi(self, "RestApi",
            handler=example_lambda,
            rest_api_name="Example-Rest-Api",
            description="Description For Example Rest API",
            proxy=False,                                            #  If not provided, default is True
            deploy = True,
            deploy_options = {
                "stage_name": "prod"                                #  If not provided, default stage name is 'prod'
            },
            endpoint_configuration=apigw.EndpointConfiguration(
                types=[apigw.EndpointType.REGIONAL]
                ),
            integration_options=apigw.LambdaIntegrationOptions(
                allow_test_invoke=False                              #  If not provided, default is True, which allows testing the integration  
                )
        )

        # Add Resource
        resource = api.root.add_resource("example-resource")

        # Add Method
        resource.add_method(
            "POST",
            api_key_required=True,
            integration=apigw.LambdaIntegration(
                handler=example_lambda,
                allow_test_invoke=False
                )
        )

        # Create API Key
        api_key = api.add_api_key("ApiKey",
            api_key_name="example-rest-api-key",
            description="Description for Example Rest API"
        )

        # Add Usage Plan
        usage_plan = api.add_usage_plan("UsagePlan",
            name="example-rest-api-key-usage-plan",
            description="Usage plan for Example Rest API Key",
            api_stages = [
                {
                    "api": api,
                    "stage": api.deployment_stage
                }
            ]
        )

        # Assign the API Key to the Usage Plan
        usage_plan.add_api_key(api_key)
