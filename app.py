#!/usr/bin/env python3
"""
HR Employee Profile Manager Lab - CDK Application Entry Point

This application deploys a comprehensive AWS training environment demonstrating
secure infrastructure patterns using CDK Python.
"""

import os
import aws_cdk as cdk

# Import stacks (will be created in subsequent tasks)
# from infra.stacks.network_stack import NetworkStack
# from infra.stacks.security_stack import SecurityStack
# from infra.stacks.storage_stack import StorageStack
# from infra.stacks.data_stack import DataStack
# from infra.stacks.secrets_stack import SecretsStack
# from infra.stacks.compute_stack import ComputeStack


app = cdk.App()

# Get configuration from context
deployment_id = app.node.try_get_context("deployment_id")
owner = app.node.try_get_context("owner")
allowed_ingress_cidr = app.node.try_get_context("allowed_ingress_cidr")
nat_mode = app.node.try_get_context("nat_mode")
db_multi_az = app.node.try_get_context("db_multi_az")
ec2_instance_type = app.node.try_get_context("ec2_instance_type")
db_instance_class = app.node.try_get_context("db_instance_class")

# Validate required parameters
if not deployment_id:
    raise ValueError("deployment_id context parameter is required")
if not owner:
    raise ValueError("owner context parameter is required")

# Common tags for all resources
common_tags = {
    "Project": "HRAppLab",
    "DeploymentID": deployment_id,
    "Owner": owner
}

# Get AWS account and region from environment
env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
)

# Stack deployment will be implemented in subsequent tasks
# Example structure:
#
# network_stack = NetworkStack(
#     app, f"hrapp-{deployment_id}-network",
#     deployment_id=deployment_id,
#     nat_mode=nat_mode,
#     allowed_ingress_cidr=allowed_ingress_cidr,
#     env=env,
#     tags=common_tags
# )
#
# security_stack = SecurityStack(
#     app, f"hrapp-{deployment_id}-security",
#     deployment_id=deployment_id,
#     env=env,
#     tags=common_tags
# )
#
# storage_stack = StorageStack(
#     app, f"hrapp-{deployment_id}-storage",
#     deployment_id=deployment_id,
#     env=env,
#     tags=common_tags
# )
#
# data_stack = DataStack(
#     app, f"hrapp-{deployment_id}-data",
#     deployment_id=deployment_id,
#     vpc=network_stack.vpc,
#     db_security_group=network_stack.rds_security_group,
#     private_subnets=network_stack.private_subnets,
#     db_multi_az=db_multi_az,
#     db_instance_class=db_instance_class,
#     env=env,
#     tags=common_tags
# )
#
# secrets_stack = SecretsStack(
#     app, f"hrapp-{deployment_id}-secrets",
#     deployment_id=deployment_id,
#     rds_instance=data_stack.rds_instance,
#     env=env,
#     tags=common_tags
# )
#
# compute_stack = ComputeStack(
#     app, f"hrapp-{deployment_id}-compute",
#     deployment_id=deployment_id,
#     vpc=network_stack.vpc,
#     alb_security_group=network_stack.alb_security_group,
#     ec2_security_group=network_stack.ec2_security_group,
#     public_subnets=network_stack.public_subnets,
#     private_subnets=network_stack.private_subnets,
#     s3_bucket=storage_stack.bucket,
#     db_secret=secrets_stack.db_secret,
#     ec2_instance_type=ec2_instance_type,
#     env=env,
#     tags=common_tags
# )

app.synth()
