#!/usr/bin/env python3

from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_dynamodb as _ddb
from aws_cdk import core


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, stack_prefix:str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Model all required resources
        ddb_table = _ddb.Table(
            self,
            id='{}-data'.format(stack_prefix),
            table_name='{}-data'.format(stack_prefix),
            partition_key=_ddb.Attribute(name='ID',
                                         type=_ddb.AttributeType.STRING),
            removal_policy=core.RemovalPolicy.DESTROY, # THIS IS NOT RECOMMENDED FOR PRODUCTION USE
            read_capacity=1,
            write_capacity=1)
        
        ## IAM Roles
        apprunner_role = _iam.Role(
            self,
            id='{}-apprunner-role'.format(stack_prefix),
            assumed_by=_iam.ServicePrincipal('tasks.apprunner.amazonaws.com'))

        # Add role for DynamoDB
        dynamodb_policy_statement = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW)
        dynamodb_policy_statement.add_actions("dynamodb:PutItem")
        dynamodb_policy_statement.add_actions("dynamodb:GetItem")
        dynamodb_policy_statement.add_actions("dynamodb:Scan")
        dynamodb_policy_statement.add_actions("dynamodb:Query")
        dynamodb_policy_statement.add_actions("dynamodb:ConditionCheckItem")
        dynamodb_policy_statement.add_actions("dynamodb:UpdateItem")
        dynamodb_policy_statement.add_resources(ddb_table.table_arn)
        apprunner_role.add_to_policy(dynamodb_policy_statement)

        
        core.CfnOutput(self, "{}-output-appRunner-role".format(stack_prefix), value=apprunner_role.role_name, export_name="{}-appRunner-role".format(stack_prefix))

env = core.Environment(region="us-east-1")

stack_prefix='apprunner-demo'
app = core.App()
stack = CdkStack(app, stack_prefix, stack_prefix=stack_prefix, env = env)
core.Tags.of(stack).add('Name',stack_prefix)

app.synth()
