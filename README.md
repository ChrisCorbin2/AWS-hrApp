# HR Employee Profile Manager Lab

A comprehensive AWS training environment demonstrating secure infrastructure patterns using AWS CDK (Python).

## Overview

This lab deploys a multi-tier web application with:
- Secure networking (VPC with public/private subnets)
- Private compute resources (EC2 in private subnets)
- Application-managed authentication (bcrypt password hashing)
- Encrypted data storage (RDS PostgreSQL, S3)
- Least-privilege IAM roles
- Secrets management with automatic rotation
- Security monitoring (Inspector, Security Hub)

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Python 3.11 or later
- Node.js 14.x or later (for CDK CLI)

## Project Structure

```
.
├── app.py                      # CDK application entry point
├── cdk.json                    # CDK configuration with context parameters
├── requirements.txt            # Python dependencies
├── infra/                      # Infrastructure code
│   └── stacks/                 # CDK stack definitions
│       ├── network_stack.py    # VPC, subnets, security groups
│       ├── security_stack.py   # Inspector, Security Hub
│       ├── storage_stack.py    # S3 bucket
│       ├── data_stack.py       # RDS PostgreSQL
│       ├── secrets_stack.py    # Secrets Manager
│       └── compute_stack.py    # EC2, ALB, IAM
├── app/                        # Flask application code
├── scripts/                    # Helper scripts
└── tests/                      # Test suite
```

## Configuration Parameters

Edit `cdk.json` to customize your deployment:

- `deployment_id`: Unique identifier for your deployment (e.g., "team01")
- `owner`: Owner tag for resources
- `allowed_ingress_cidr`: CIDR block allowed to access ALB (default: "0.0.0.0/0")
- `nat_mode`: "single" or "dual" NAT Gateway configuration
- `db_multi_az`: Enable Multi-AZ for RDS (true/false)
- `ec2_instance_type`: EC2 instance type (default: "t3.micro")
- `db_instance_class`: RDS instance class (default: "db.t3.micro")

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Deployment

1. Bootstrap CDK (first time only):
   ```bash
   cdk bootstrap
   ```

2. Synthesize CloudFormation templates:
   ```bash
   cdk synth
   ```

3. Deploy all stacks:
   ```bash
   cdk deploy --all
   ```

4. Deploy specific stack:
   ```bash
   cdk deploy hrapp-{deployment_id}-network
   ```

## Verification

After deployment, verify the infrastructure:

1. Check stack outputs:
   ```bash
   aws cloudformation describe-stacks --stack-name hrapp-{deployment_id}-compute
   ```

2. Access the application via ALB DNS name (from stack outputs)

3. Verify security monitoring in AWS Console:
   - Amazon Inspector: Check for vulnerability findings
   - Security Hub: Review aggregated security findings

## Cost Considerations

Default configuration optimized for training/development:
- Single NAT Gateway (~$32/month)
- Single-AZ RDS db.t3.micro (~$15/month)
- 2x EC2 t3.micro instances (~$15/month)
- S3, data transfer, and other services (variable)

**Estimated monthly cost: ~$65-80**

For production-like high availability:
- Set `nat_mode: "dual"` (adds ~$32/month)
- Set `db_multi_az: true` (doubles RDS cost)

## Cleanup

To avoid ongoing charges, destroy all resources:

```bash
cdk destroy --all
```

## Documentation

See the `docs/` directory for detailed documentation:
- Architecture diagrams and design decisions
- Security considerations
- Cost analysis
- Troubleshooting guide
- Vulnerability detection walkthrough

## License

This project is for educational purposes.
