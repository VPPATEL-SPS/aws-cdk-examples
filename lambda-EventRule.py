from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam
)
import aws_cdk as core
import os
from constructs import Construct

class ExampleLambdaStack(Stack):
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

        # Create the AWS Event Rule
        event_rule = events.Rule(
            self, "ExampleEventRule",
            rule_name="Example-Event-Rule",
            description="Description for the Event Rule",
            event_pattern = {
                "source": ["aws.ssm"],
                "detail_type": ["Maintenance Window Execution State-change Notification"]
            }
        )

        # Add the lambda function as a target to the rule
        ssm_mw_rule.add_target(targets.LambdaFunction(example_lambda))


        # Create an Scheduler Event Rule
        scheduler_rule = events.Rule(
            self, "ExampleSchedulerRule",
            rule_name="Example-Scheduler-Rule",
            description="Description for the Scheduler Event Rule",
            schedule=Schedule.rate(core.Duration.minutes(1))       
            # schedule=events.Schedule.cron( minute="0",hour="16",month="*",week_day="WED",year="*")
        )

        # Add the lambda function as a target to the rule
        ssm_mw_rule.add_target(targets.LambdaFunction(example_lambda))
