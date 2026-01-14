# Requirements Document

## Introduction

This document specifies the requirements for an HR Employee Profile Manager Lab - a comprehensive training environment that demonstrates secure AWS infrastructure patterns using CDK (Python). The lab showcases secure networking, private compute, application-managed authentication, private data storage, least-privilege IAM, secrets management with rotation, and security monitoring with Inspector and Security Hub.

## Glossary

- **HR_App**: The employee profile management web application
- **CDK_Stack**: AWS Cloud Development Kit infrastructure-as-code stack
- **ALB**: Application Load Balancer
- **NAT_Gateway**: Network Address Translation gateway for private subnet internet access
- **RDS_Instance**: Relational Database Service PostgreSQL instance
- **Secrets_Manager**: AWS service for managing database credentials
- **Inspector**: AWS vulnerability scanning service for EC2 instances
- **Security_Hub**: AWS security findings aggregation service
- **SSM_Session_Manager**: AWS Systems Manager Session Manager for secure EC2 access
- **Deployment_ID**: Unique identifier for parallel team deployments (e.g., team01, team02)
- **Private_Subnet**: VPC subnet with no direct internet access, using NAT for egress
- **Public_Subnet**: VPC subnet with internet gateway access

## Requirements

### Requirement 1: Infrastructure as Code Foundation

**User Story:** As a DevOps engineer, I want to deploy the entire infrastructure using AWS CDK Python, so that the lab environment is reproducible and version-controlled.

#### Acceptance Criteria

1. THE CDK_Stack SHALL be written in Python
2. WHEN a deployment is initiated, THE CDK_Stack SHALL create all AWS resources in the correct dependency order
3. THE CDK_Stack SHALL support multiple parallel deployments through Deployment_ID parameter
4. THE CDK_Stack SHALL apply consistent tagging with Project, DeploymentID, and Owner tags to all resources
5. THE CDK_Stack SHALL use naming convention hrapp-<deploymentid>-<resource> for all resources
6. THE CDK_Stack SHALL accept configuration parameters for deploymentid, owner, allowed_ingress_cidr, region, nat_mode, and db_multi_az

### Requirement 2: Secure Network Architecture

**User Story:** As a security architect, I want a multi-tier VPC with public and private subnets across multiple availability zones, so that the application follows AWS security best practices.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a VPC spanning 2 availability zones
2. THE CDK_Stack SHALL create public subnets in each availability zone for the ALB
3. THE CDK_Stack SHALL create private subnets in each availability zone for EC2 and RDS
4. THE CDK_Stack SHALL attach an Internet Gateway to the VPC for public subnet internet access
5. WHEN nat_mode is set to single, THE CDK_Stack SHALL create one NAT Gateway in a single availability zone
6. WHEN nat_mode is set to dual, THE CDK_Stack SHALL create NAT Gateways in both availability zones
7. THE CDK_Stack SHALL configure route tables directing private subnet traffic through NAT Gateway for internet egress
8. THE CDK_Stack SHALL configure route tables directing public subnet traffic through Internet Gateway

### Requirement 3: Security Group Configuration

**User Story:** As a security engineer, I want properly configured security groups with least-privilege network access, so that traffic is restricted to only necessary paths.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a security group for the ALB allowing inbound HTTPS/HTTP from allowed_ingress_cidr
2. THE CDK_Stack SHALL create a security group for EC2 instances allowing inbound traffic only from the ALB security group
3. THE CDK_Stack SHALL create a security group for RDS allowing inbound PostgreSQL traffic only from the EC2 security group
4. THE CDK_Stack SHALL configure EC2 security group to allow outbound traffic to RDS on port 5432
5. THE CDK_Stack SHALL configure EC2 security group to allow outbound HTTPS traffic for AWS API calls and package downloads
6. THE CDK_Stack SHALL NOT allow direct SSH access to EC2 instances

### Requirement 4: Private RDS PostgreSQL Database

**User Story:** As a database administrator, I want a private RDS PostgreSQL instance in private subnets, so that the database is not accessible from the internet.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create an RDS PostgreSQL instance in private subnets
2. THE RDS_Instance SHALL NOT be publicly accessible
3. WHEN db_multi_az is true, THE RDS_Instance SHALL be deployed in multi-AZ configuration
4. WHEN db_multi_az is false, THE RDS_Instance SHALL be deployed in single-AZ configuration
5. THE RDS_Instance SHALL use encryption at rest
6. THE RDS_Instance SHALL have automated backups enabled
7. THE RDS_Instance SHALL use credentials stored in Secrets_Manager

### Requirement 5: Database Schema and Structure

**User Story:** As an application developer, I want database tables for users and employee profiles, so that the application can store authentication data and employee information.

#### Acceptance Criteria

1. THE database schema SHALL include a users table with columns for id, username, password_hash, created_at
2. THE database schema SHALL include an employees table with columns for id, name, role, department, image_s3_key, image_url, user_id, created_at, updated_at
3. THE users table password_hash column SHALL store bcrypt-hashed passwords
4. THE employees table SHALL have a foreign key relationship to the users table

### Requirement 6: AWS Secrets Manager Integration

**User Story:** As a security engineer, I want database credentials managed by AWS Secrets Manager with automatic rotation, so that credentials are never hardcoded and are regularly rotated.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a secret in Secrets_Manager containing RDS master credentials
2. THE Secrets_Manager secret SHALL have automatic rotation enabled
3. THE Secrets_Manager secret SHALL rotate credentials every 30 days
4. THE CDK_Stack SHALL configure the RDS_Instance to use the Secrets_Manager secret for master credentials
5. THE EC2 IAM role SHALL have permission to read only the specific secret for its deployment
6. THE HR_App SHALL retrieve database credentials from Secrets_Manager at startup
7. WHEN a database authentication failure occurs, THE HR_App SHALL re-fetch credentials from Secrets_Manager and retry connection

### Requirement 7: Private S3 Bucket for Image Storage

**User Story:** As a security engineer, I want a private S3 bucket with encryption and public access blocked, so that employee profile images are stored securely.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create an S3 bucket with naming convention hrapp-<deploymentid>-uploads
2. THE S3 bucket SHALL have all public access blocked
3. THE S3 bucket SHALL use server-side encryption with AWS managed keys
4. THE S3 bucket SHALL have versioning enabled
5. THE EC2 IAM role SHALL have permission to PutObject only under the uploads/* prefix
6. THE EC2 IAM role SHALL have permission to GetObject from the uploads/* prefix
7. THE S3 bucket SHALL NOT allow public read access

### Requirement 8: Least-Privilege IAM Roles

**User Story:** As a security engineer, I want EC2 instances to use IAM roles with minimal required permissions, so that the principle of least privilege is enforced.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create an IAM role for EC2 instances
2. THE EC2 IAM role SHALL include the AmazonSSMManagedInstanceCore managed policy for SSM Session Manager access
3. THE EC2 IAM role SHALL have permission to read the specific Secrets_Manager secret for database credentials
4. THE EC2 IAM role SHALL have permission to PutObject and GetObject in the S3 bucket under uploads/* prefix only
5. THE EC2 IAM role SHALL have permission to write logs to CloudWatch Logs for the application log group
6. THE EC2 IAM role SHALL NOT have administrator or power user permissions

### Requirement 9: EC2 Compute in Private Subnets

**User Story:** As a DevOps engineer, I want EC2 instances running in private subnets with SSM Session Manager access, so that the application is not directly exposed to the internet.

#### Acceptance Criteria

1. THE CDK_Stack SHALL launch EC2 instances in private subnets
2. THE EC2 instances SHALL use IMDSv2 (Instance Metadata Service version 2) only
3. THE EC2 instances SHALL have the IAM role attached for AWS service access
4. THE EC2 instances SHALL be accessible via SSM_Session_Manager only
5. THE EC2 instances SHALL NOT have public IP addresses
6. THE EC2 instances SHALL use user data script to install application dependencies and configure the application

### Requirement 10: Application Load Balancer

**User Story:** As a DevOps engineer, I want an Application Load Balancer in public subnets forwarding traffic to EC2 instances, so that users can access the application via a public endpoint.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create an ALB in public subnets across multiple availability zones
2. THE ALB SHALL have a listener on port 80 (HTTP)
3. THE ALB SHALL forward traffic to a target group containing EC2 instances
4. THE ALB target group SHALL perform health checks on the /health endpoint
5. THE ALB target group SHALL use HTTP protocol on the application port
6. WHEN health checks fail, THE ALB SHALL mark instances as unhealthy and stop routing traffic to them
7. THE ALB SHALL be accessible from IP addresses specified in allowed_ingress_cidr parameter

### Requirement 11: Application-Managed Authentication

**User Story:** As an application developer, I want user authentication managed by the application using bcrypt password hashing, so that users can securely log in without requiring AWS Cognito.

#### Acceptance Criteria

1. THE HR_App SHALL provide a /register endpoint for user registration
2. WHEN a user registers, THE HR_App SHALL hash the password using bcrypt before storing in the database
3. THE HR_App SHALL provide a /login endpoint for user authentication
4. WHEN a user logs in, THE HR_App SHALL verify the password against the bcrypt hash stored in the database
5. WHEN authentication succeeds, THE HR_App SHALL create a session and set a session cookie
6. THE session cookie SHALL have HttpOnly flag set
7. THE session cookie SHALL have SameSite attribute set to Lax
8. WHEN TLS is enabled, THE session cookie SHALL have Secure flag set

### Requirement 12: Employee Profile Management

**User Story:** As an authenticated user, I want to create employee profiles with name, role, department, and profile image, so that employee information is stored in the system.

#### Acceptance Criteria

1. THE HR_App SHALL provide an endpoint for creating employee profiles
2. WHEN creating an employee profile, THE HR_App SHALL require authentication
3. THE HR_App SHALL accept employee name, role, department, and image file in the profile creation request
4. WHEN an image is uploaded, THE HR_App SHALL store the image in S3 under uploads/<deploymentid>/<uuid>.<extension>
5. WHEN an image is uploaded, THE HR_App SHALL store the S3 key and a reference URL in the RDS employees table
6. THE HR_App SHALL associate the employee profile with the authenticated user
7. THE HR_App SHALL provide an endpoint to retrieve employee profiles for authenticated users

### Requirement 13: Health Check Endpoint

**User Story:** As a DevOps engineer, I want a health check endpoint that the ALB can use to determine instance health, so that unhealthy instances are removed from the load balancer.

#### Acceptance Criteria

1. THE HR_App SHALL provide a /health endpoint
2. WHEN the /health endpoint is accessed, THE HR_App SHALL return HTTP 200 status code if the application is healthy
3. THE /health endpoint SHALL verify database connectivity before returning healthy status
4. WHEN database connectivity fails, THE /health endpoint SHALL return HTTP 503 status code

### Requirement 14: Secrets Manager Credential Rotation Handling

**User Story:** As an application developer, I want the application to handle Secrets Manager credential rotation gracefully, so that the application continues functioning when credentials are rotated.

#### Acceptance Criteria

1. THE HR_App SHALL cache database credentials retrieved from Secrets_Manager
2. WHEN a database authentication error occurs, THE HR_App SHALL re-fetch credentials from Secrets_Manager
3. WHEN credentials are re-fetched, THE HR_App SHALL retry the failed database operation
4. THE HR_App SHALL log credential rotation events for monitoring
5. THE HR_App SHALL NOT crash or become unavailable during credential rotation

### Requirement 15: Amazon Inspector Integration

**User Story:** As a security engineer, I want Amazon Inspector enabled to scan EC2 instances for vulnerabilities, so that security issues are automatically detected.

#### Acceptance Criteria

1. THE CDK_Stack SHALL enable Amazon Inspector for the AWS account
2. THE Inspector configuration SHALL include EC2 scanning
3. THE Inspector SHALL scan EC2 instances for package vulnerabilities
4. THE Inspector SHALL scan EC2 instances for network reachability issues
5. THE Inspector findings SHALL be published to Security_Hub

### Requirement 16: AWS Security Hub Integration

**User Story:** As a security engineer, I want AWS Security Hub enabled to aggregate security findings, so that all security issues are visible in a central location.

#### Acceptance Criteria

1. THE CDK_Stack SHALL enable Security_Hub for the AWS account
2. THE Security_Hub SHALL ingest findings from Inspector
3. THE Security_Hub SHALL provide a consolidated view of all security findings
4. THE Security_Hub SHALL categorize findings by severity

### Requirement 17: Vulnerability Introduction and Remediation

**User Story:** As a security trainer, I want to demonstrate vulnerability detection by intentionally installing an outdated package, so that trainees can see the security monitoring workflow.

#### Acceptance Criteria

1. THE deployment SHALL include a script to install an intentionally outdated package on EC2 instances
2. WHEN the outdated package is installed, THE Inspector SHALL detect the vulnerability within its scan cycle
3. WHEN the vulnerability is detected, THE Inspector finding SHALL appear in Security_Hub
4. THE deployment SHALL include documentation on how to remediate the vulnerability
5. THE deployment SHALL include a script to update the outdated package and verify remediation

### Requirement 18: Deployment Configuration and Flexibility

**User Story:** As a training administrator, I want configurable deployment options for cost control, so that multiple teams can deploy the lab with appropriate resource sizing.

#### Acceptance Criteria

1. THE CDK_Stack SHALL accept a nat_mode parameter with values "single" or "dual"
2. THE CDK_Stack SHALL accept a db_multi_az parameter with boolean values
3. THE CDK_Stack SHALL use single NAT Gateway and single-AZ RDS as default for cost optimization
4. THE CDK_Stack SHALL support deployment of multiple independent environments using different Deployment_ID values
5. WHEN different Deployment_ID values are used, THE resources SHALL NOT conflict or interfere with each other

### Requirement 19: Systemd Service Management

**User Story:** As a DevOps engineer, I want the application to run as a systemd service on EC2, so that the application starts automatically and restarts on failure.

#### Acceptance Criteria

1. THE EC2 user data script SHALL create a systemd service unit file for the HR_App
2. THE systemd service SHALL start the HR_App on system boot
3. THE systemd service SHALL restart the HR_App automatically on failure
4. THE systemd service SHALL set required environment variables for the application
5. THE systemd service SHALL run the application on a configurable APP_PORT

### Requirement 20: Documentation and Verification

**User Story:** As a trainee, I want comprehensive documentation with deployment steps and verification checklists, so that I can successfully deploy and validate the lab environment.

#### Acceptance Criteria

1. THE repository SHALL include a README.md with prerequisites, deployment steps, and verification checklist
2. THE documentation SHALL include architecture diagrams and decision rationale
3. THE documentation SHALL include cost considerations and optimization options
4. THE documentation SHALL include security considerations for app-managed authentication
5. THE documentation SHALL include a walkthrough for the vulnerability introduction, detection, and remediation process
6. THE documentation SHALL include troubleshooting guidance for common deployment issues
7. THE repository SHALL include helper scripts for database schema initialization and admin user seeding
