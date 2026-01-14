# Implementation Plan: HR Employee Profile Manager Lab

## Overview

This implementation plan breaks down the HR Employee Profile Manager Lab into discrete, incremental tasks. The approach follows a bottom-up strategy: infrastructure first (networking, security, data, storage), then compute and application deployment, followed by testing and security validation.

Each task builds on previous work, ensuring that core functionality is validated early through code and tests. The plan supports parallel team deployments through parameterized infrastructure and consistent resource tagging.

## Tasks

- [x] 1. Set up CDK project structure and configuration
  - Create CDK Python project with proper directory structure
  - Configure cdk.json with context parameters (deployment_id, owner, allowed_ingress_cidr, nat_mode, db_multi_az)
  - Set up requirements.txt with CDK dependencies
  - Create app.py as CDK entry point
  - Initialize Git repository with .gitignore
  - _Requirements: 1.1, 1.6_

- [ ] 2. Implement NetworkStack for VPC and networking
  - [ ] 2.1 Create NetworkStack class with VPC spanning 2 AZs
    - Create VPC with CIDR 10.0.0.0/16
    - Enable DNS support and DNS hostnames
    - Create 2 public subnets (10.0.1.0/24, 10.0.2.0/24)
    - Create 2 private subnets (10.0.11.0/24, 10.0.12.0/24)
    - Attach Internet Gateway to VPC
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ] 2.2 Configure NAT Gateway(s) based on nat_mode parameter
    - Create Elastic IP(s) for NAT Gateway(s)
    - Create 1 NAT Gateway when nat_mode="single" (in AZ1)
    - Create 2 NAT Gateways when nat_mode="dual" (one per AZ)
    - Configure route tables for private subnets to route through NAT
    - Configure route tables for public subnets to route through IGW
    - _Requirements: 2.5, 2.6, 2.7, 2.8_

  - [ ] 2.3 Create security groups for ALB, EC2, and RDS
    - Create ALB security group allowing HTTP/HTTPS from allowed_ingress_cidr
    - Create EC2 security group allowing traffic from ALB security group only
    - Create RDS security group allowing PostgreSQL (5432) from EC2 security group only
    - Configure EC2 egress to RDS, HTTPS (443), and HTTP (80)
    - Ensure no SSH (port 22) ingress rules
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 2.4 Add resource tagging and naming
    - Apply tags: Project=HRAppLab, DeploymentID, Owner to all resources
    - Use naming convention: hrapp-{deployment_id}-{resource}
    - Export VPC ID, subnet IDs, security group IDs as stack outputs
    - _Requirements: 1.4, 1.5_

  - [ ]* 2.5 Write CDK snapshot tests for NetworkStack
    - Test VPC resource count
    - Test subnet count (4 total: 2 public, 2 private)
    - Test NAT Gateway count based on nat_mode parameter
    - Test security group count (3 total)
    - Test resource tagging
    - _Requirements: 1.2, 1.4, 1.5_

- [ ] 3. Implement SecurityStack for Inspector and Security Hub
  - [ ] 3.1 Enable Amazon Inspector for EC2 scanning
    - Enable Inspector2 for the account
    - Configure EC2 scanning for package vulnerabilities
    - Configure network reachability scanning
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

  - [ ] 3.2 Enable AWS Security Hub
    - Enable Security Hub for the account
    - Enable AWS Foundational Security Best Practices standard
    - Configure Inspector integration to publish findings to Security Hub
    - Export Inspector ARN and Security Hub ARN as outputs
    - _Requirements: 15.5, 16.1, 16.2_

  - [ ]* 3.3 Write CDK snapshot tests for SecurityStack
    - Test Inspector enablement
    - Test Security Hub enablement
    - _Requirements: 15.1, 16.1_

- [ ] 4. Implement StorageStack for S3 bucket
  - [ ] 4.1 Create private S3 bucket for image uploads
    - Create bucket with name: hrapp-{deployment_id}-uploads-{account_id}
    - Enable server-side encryption (SSE-S3)
    - Enable versioning
    - Block all public access
    - Apply resource tags
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.7_

  - [ ] 4.2 Configure bucket policy for least-privilege access
    - Deny all public access explicitly
    - Export bucket name and ARN as outputs (for IAM policy in ComputeStack)
    - _Requirements: 7.7_

  - [ ]* 4.3 Write CDK snapshot tests for StorageStack
    - Test bucket creation
    - Test encryption configuration
    - Test versioning enabled
    - Test public access block settings
    - _Requirements: 7.2, 7.3, 7.4_

- [ ] 5. Implement DataStack for RDS PostgreSQL
  - [ ] 5.1 Create RDS PostgreSQL instance in private subnets
    - Create DB subnet group using private subnets from NetworkStack
    - Create RDS PostgreSQL 15.x instance
    - Use instance class from context (default: db.t3.micro)
    - Configure storage: 20 GB GP3
    - Set publicly_accessible to false
    - Enable encryption at rest
    - Enable automated backups (7-day retention)
    - Configure Multi-AZ based on db_multi_az parameter
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 5.2 Generate master credentials and prepare for Secrets Manager
    - Generate random master username
    - Generate random master password (will be stored in Secrets Manager)
    - Set initial database name to "hrappdb"
    - Apply resource tags
    - Export RDS endpoint, port, database name, and instance identifier
    - _Requirements: 4.7_

  - [ ]* 5.3 Write CDK snapshot tests for DataStack
    - Test RDS instance creation
    - Test subnet group configuration
    - Test encryption enabled
    - Test publicly_accessible is false
    - Test Multi-AZ configuration based on parameter
    - _Requirements: 4.1, 4.2, 4.5_

- [ ] 6. Implement SecretsStack for credential management
  - [ ] 6.1 Create Secrets Manager secret for RDS credentials
    - Create secret containing: username, password, engine, host, port, dbname
    - Use RDS-generated credentials from DataStack
    - Enable automatic rotation with 30-day schedule
    - Configure rotation using RDS single-user rotation strategy
    - Apply resource tags
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ] 6.2 Export secret ARN for EC2 IAM role
    - Export secret ARN as stack output
    - Export secret name as stack output
    - _Requirements: 6.5_

  - [ ]* 6.3 Write CDK snapshot tests for SecretsStack
    - Test secret creation
    - Test rotation configuration
    - Test rotation schedule (30 days)
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 7. Checkpoint - Verify infrastructure stacks synthesize correctly
  - Run `cdk synth` to generate CloudFormation templates
  - Review templates for correct dependencies
  - Ensure all stack outputs are properly exported
  - Run CDK snapshot tests
  - Ask user if questions arise

- [ ] 8. Implement ComputeStack - IAM roles
  - [ ] 8.1 Create EC2 IAM role with least-privilege permissions
    - Create IAM role for EC2 instances
    - Attach AmazonSSMManagedInstanceCore managed policy
    - Create inline policy for Secrets Manager read access (specific secret only)
    - Create inline policy for S3 access (PutObject/GetObject under uploads/* only)
    - Create inline policy for CloudWatch Logs write access
    - Ensure no admin or power user permissions
    - Apply resource tags
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ]* 8.2 Write unit tests for IAM policy validation
    - Test that role includes SSM managed policy
    - Test that role can read specific secret only
    - Test that role can access S3 under uploads/* only
    - Test that role does not have admin permissions
    - _Requirements: 8.2, 8.3, 8.4, 8.6_

- [ ] 9. Create Flask application structure
  - [ ] 9.1 Set up Flask application directory structure
    - Create /app directory with subdirectories
    - Create app.py (main Flask application)
    - Create config.py (configuration from environment variables)
    - Create db.py (database connection with Secrets Manager integration)
    - Create auth.py (authentication logic with bcrypt)
    - Create storage.py (S3 upload/download logic)
    - Create requirements.txt (Flask, psycopg2-binary, boto3, bcrypt)
    - _Requirements: 11.1, 11.3, 12.1_

  - [ ] 9.2 Implement configuration management
    - Read environment variables: APP_PORT, SECRET_KEY, DB_SECRET_ARN, S3_BUCKET_NAME, DEPLOYMENT_ID, AWS_REGION
    - Validate required environment variables on startup
    - _Requirements: 19.4_

  - [ ] 9.3 Implement database connection with credential rotation handling
    - Create DatabaseConnection class
    - Implement get_secret() method with 5-minute caching
    - Implement connect() method with retry on auth failure
    - Implement credential refresh on authentication errors
    - Add logging for credential rotation events
    - _Requirements: 6.6, 6.7, 14.1, 14.2, 14.3, 14.4_

  - [ ]* 9.4 Write property test for credential rotation resilience
    - **Property 7: Credential Rotation Resilience**
    - **Validates: Requirements 6.7, 14.2, 14.3, 14.5**
    - Test that auth failures trigger credential refresh
    - Test that operations retry after refresh
    - Test that application remains available during rotation
    - _Requirements: 6.7, 14.2, 14.3, 14.5_

- [ ] 10. Implement authentication endpoints
  - [ ] 10.1 Implement password hashing with bcrypt
    - Create hash_password() function using bcrypt with work factor 12
    - Create verify_password() function
    - Ensure passwords are never logged
    - _Requirements: 11.2, 5.3_

  - [ ] 10.2 Implement /register endpoint
    - Accept JSON with username and password
    - Validate username length (minimum 3 characters)
    - Hash password with bcrypt
    - Insert user into database
    - Return 201 Created with user ID
    - Return 400 if username exists
    - _Requirements: 11.1, 11.2_

  - [ ] 10.3 Implement /login endpoint
    - Accept JSON with username and password
    - Query user from database
    - Verify password against bcrypt hash
    - Create session on success
    - Set session cookie with HttpOnly, SameSite=Lax
    - Return 200 OK on success, 401 on failure
    - _Requirements: 11.3, 11.4, 11.5, 11.6, 11.7_

  - [ ] 10.4 Implement /logout endpoint
    - Require authentication
    - Clear session
    - Return 200 OK
    - _Requirements: 11.3_

  - [ ]* 10.5 Write property test for password hash security
    - **Property 3: Password Hash Security**
    - **Validates: Requirements 5.3, 11.2**
    - Test that all passwords are hashed with bcrypt
    - Test that stored hashes match bcrypt format
    - Test password round-trip (hash then verify)
    - _Requirements: 5.3, 11.2_

  - [ ]* 10.6 Write property test for authentication verification
    - **Property 4: Authentication Verification**
    - **Validates: Requirements 11.4**
    - Test that correct passwords succeed
    - Test that incorrect passwords fail
    - Test with various password inputs
    - _Requirements: 11.4_

  - [ ]* 10.7 Write unit tests for authentication endpoints
    - Test /register with valid input
    - Test /register with duplicate username
    - Test /login with correct credentials
    - Test /login with incorrect credentials
    - Test session cookie attributes
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.6, 11.7_

- [ ] 11. Implement employee profile endpoints
  - [ ] 11.1 Implement S3 upload functionality
    - Create upload_image() function
    - Generate UUID for filename
    - Create S3 key: uploads/{deployment_id}/{uuid}.{extension}
    - Upload to S3 with proper content type
    - Return S3 key
    - Handle S3 errors (AccessDenied, NoSuchBucket)
    - _Requirements: 12.4_

  - [ ] 11.2 Implement POST /employees endpoint
    - Require authentication (check session)
    - Accept multipart form: name, role, department, image file
    - Validate required fields
    - Upload image to S3
    - Insert employee record into database with S3 key and user_id
    - Return 201 Created with employee ID
    - Return 401 if not authenticated
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

  - [ ] 11.3 Implement GET /employees endpoint
    - Require authentication
    - Query employees for authenticated user
    - Generate presigned URLs for images
    - Return JSON array of employee objects
    - Return 401 if not authenticated
    - _Requirements: 12.7_

  - [ ] 11.4 Implement GET /employees/{id} endpoint
    - Require authentication
    - Query specific employee
    - Generate presigned URL for image
    - Return JSON employee object
    - Return 404 if not found
    - Return 401 if not authenticated
    - _Requirements: 12.7_

  - [ ]* 11.5 Write property test for authenticated endpoint protection
    - **Property 5: Authenticated Endpoint Protection**
    - **Validates: Requirements 12.2**
    - Test that unauthenticated requests are rejected
    - Test across all protected endpoints
    - _Requirements: 12.2_

  - [ ]* 11.6 Write property test for image upload consistency
    - **Property 6: Image Upload Consistency**
    - **Validates: Requirements 12.4, 12.5, 12.6**
    - Test S3 key format for various inputs
    - Test that database contains S3 reference after upload
    - Test that employee is associated with authenticated user
    - _Requirements: 12.4, 12.5, 12.6_

  - [ ]* 11.7 Write unit tests for employee endpoints
    - Test POST /employees with valid input
    - Test POST /employees without authentication
    - Test GET /employees returns user's employees
    - Test GET /employees/{id} returns correct employee
    - _Requirements: 12.1, 12.2, 12.7_

- [ ] 12. Implement health check endpoint
  - [ ] 12.1 Implement /health endpoint
    - Test database connectivity with SELECT 1 query
    - Return 200 OK with status "healthy" if database reachable
    - Return 503 Service Unavailable with status "unhealthy" if database unreachable
    - Log health check failures
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [ ]* 12.2 Write unit tests for health endpoint
    - Test /health returns 200 when database is healthy
    - Test /health returns 503 when database is unreachable
    - _Requirements: 13.2, 13.4_

- [ ] 13. Create database schema SQL script
  - [ ] 13.1 Create schema.sql with table definitions
    - Create users table with id, username, password_hash, created_at
    - Add unique constraint on username
    - Add check constraint for username length (>= 3)
    - Create index on username
    - Create employees table with id, name, role, department, image_s3_key, image_url, user_id, created_at, updated_at
    - Add foreign key constraint from employees.user_id to users.id with CASCADE delete
    - Add check constraint for name not empty
    - Create indexes on user_id and department
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ]* 13.2 Write validation tests for database schema
    - Test that users table exists with correct columns
    - Test that employees table exists with correct columns
    - Test that foreign key constraint exists
    - _Requirements: 5.1, 5.2, 5.4_

- [ ] 14. Checkpoint - Test application locally
  - Set up local PostgreSQL database
  - Run schema.sql to create tables
  - Set environment variables for local testing
  - Start Flask application
  - Test /health endpoint
  - Test /register and /login endpoints
  - Test /employees endpoints
  - Ask user if questions arise

- [ ] 15. Implement ComputeStack - EC2 and ALB
  - [ ] 15.1 Create EC2 user data script
    - Install Python 3.11, pip, PostgreSQL client
    - Install application dependencies from requirements.txt
    - Create /opt/hrapp directory
    - Copy application code to /opt/hrapp
    - Create systemd service unit file
    - Set environment variables in service file
    - Enable and start systemd service
    - _Requirements: 9.6, 19.1, 19.4_

  - [ ] 15.2 Create EC2 launch template
    - Use Amazon Linux 2023 AMI (latest)
    - Use instance type from context (default: t3.micro)
    - Attach IAM instance profile with EC2 role
    - Configure IMDSv2 required
    - Attach EC2 security group
    - Include user data script
    - Apply resource tags
    - _Requirements: 9.1, 9.2, 9.3, 9.5_

  - [ ] 15.3 Create Auto Scaling Group
    - Use launch template
    - Deploy in private subnets
    - Desired capacity: 2, Min: 1, Max: 4
    - Health check type: ELB
    - Health check grace period: 300 seconds
    - Apply resource tags
    - _Requirements: 9.1_

  - [ ] 15.4 Create Application Load Balancer
    - Deploy in public subnets across both AZs
    - Attach ALB security group
    - Create target group: HTTP protocol, port 5000
    - Configure health check: path=/health, interval=30s, timeout=5s, healthy=2, unhealthy=3
    - Create listener on port 80 forwarding to target group
    - Register Auto Scaling Group with target group
    - Apply resource tags
    - Export ALB DNS name as output
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7_

  - [ ]* 15.5 Write CDK snapshot tests for ComputeStack
    - Test IAM role creation
    - Test launch template configuration
    - Test Auto Scaling Group configuration
    - Test ALB creation
    - Test target group health check configuration
    - _Requirements: 8.1, 9.1, 10.1, 10.4_

- [ ] 16. Create systemd service unit file template
  - [ ] 16.1 Create hrapp.service template
    - Set Type=simple
    - Set User=ec2-user
    - Set WorkingDirectory=/opt/hrapp
    - Configure environment variables: APP_PORT, SECRET_KEY, DB_SECRET_ARN, S3_BUCKET_NAME, DEPLOYMENT_ID, AWS_REGION
    - Set ExecStart to run Flask application
    - Configure Restart=always with RestartSec=10
    - Set WantedBy=multi-user.target
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

  - [ ]* 16.2 Write validation tests for systemd configuration
    - Test that service file is created by user data
    - Test that service starts on boot
    - Test that service restarts on failure
    - _Requirements: 19.1, 19.2, 19.3_

- [ ] 17. Create helper scripts
  - [ ] 17.1 Create scripts/init_db.sh for database initialization
    - Connect to RDS using credentials from Secrets Manager
    - Run schema.sql to create tables
    - Verify tables created successfully
    - _Requirements: 20.7_

  - [ ] 17.2 Create scripts/seed_admin.sh for admin user creation
    - Accept username and password as arguments
    - Hash password with bcrypt
    - Insert admin user into database
    - _Requirements: 20.7_

  - [ ] 17.3 Create scripts/introduce_vulnerability.sh
    - Install intentionally outdated package (e.g., openssl-1.0.1e)
    - Log installation for documentation
    - _Requirements: 17.1_

  - [ ] 17.4 Create scripts/remediate_vulnerability.sh
    - Update the outdated package to latest version
    - Verify package updated
    - Log remediation for documentation
    - _Requirements: 17.5_

  - [ ] 17.5 Create scripts/validate_deployment.sh
    - Check that all stacks deployed successfully
    - Verify ALB is healthy
    - Test /health endpoint
    - Test basic authentication flow
    - _Requirements: 20.1_

- [ ] 18. Create documentation
  - [ ] 18.1 Create README.md with deployment instructions
    - List prerequisites (AWS CLI, CDK, Python 3.11, Node.js)
    - Document deployment steps (cdk bootstrap, cdk deploy)
    - Include verification checklist mapping to lab outcomes
    - Document configuration parameters
    - Include troubleshooting section
    - _Requirements: 20.1_

  - [ ] 18.2 Create docs/architecture.md
    - Include architecture diagrams (copy from design.md)
    - Document design decisions and rationale
    - Explain multi-stack approach
    - Document network architecture
    - _Requirements: 20.2_

  - [ ] 18.3 Create docs/cost_analysis.md
    - Document monthly cost estimates
    - List cost optimization options
    - Explain default configuration choices
    - Document cost monitoring setup
    - _Requirements: 20.3_

  - [ ] 18.4 Create docs/security.md
    - Document security considerations for app-managed auth
    - List compensating controls
    - Explain when to use Cognito instead
    - Document network security architecture
    - Document IAM least-privilege approach
    - _Requirements: 20.4_

  - [ ] 18.5 Create docs/vulnerability_demo.md
    - Document vulnerability introduction steps
    - Explain Inspector detection process
    - Show how findings appear in Security Hub
    - Document remediation steps
    - Include screenshots or expected outputs
    - _Requirements: 20.5_

  - [ ] 18.6 Create docs/troubleshooting.md
    - Document common deployment issues
    - List resolution steps for each issue
    - Include debugging commands
    - Document how to access EC2 via SSM Session Manager
    - _Requirements: 20.6_

- [ ] 19. Checkpoint - Deploy and validate infrastructure
  - Run `cdk bootstrap` if not already done
  - Deploy all stacks: `cdk deploy --all`
  - Verify all stacks deployed successfully
  - Run scripts/validate_deployment.sh
  - Test ALB endpoint
  - Test SSM Session Manager access to EC2
  - Ask user if questions arise

- [ ] 20. Implement integration tests
  - [ ]* 20.1 Write end-to-end workflow test
    - Test complete flow: register → login → create employee → retrieve employee
    - Verify image uploaded to S3
    - Verify employee data in database
    - _Requirements: 11.1, 11.2, 11.3, 12.1, 12.3, 12.4, 12.5_

  - [ ]* 20.2 Write ALB health check integration test
    - Test that ALB marks instances healthy when /health returns 200
    - Test that ALB marks instances unhealthy when /health returns 503
    - _Requirements: 10.6, 13.2, 13.4_

  - [ ]* 20.3 Write property test for resource metadata consistency
    - **Property 1: Resource Metadata Consistency**
    - **Validates: Requirements 1.4, 1.5**
    - Test that all resources have required tags
    - Test that all resources follow naming convention
    - _Requirements: 1.4, 1.5_

  - [ ]* 20.4 Write property test for deployment isolation
    - **Property 2: Deployment Isolation**
    - **Validates: Requirements 1.3, 18.5**
    - Test that different deployment IDs create separate resources
    - Test that resources don't conflict
    - _Requirements: 1.3, 18.5_

- [ ] 21. Implement security validation tests
  - [ ]* 21.1 Write test for vulnerability detection workflow
    - Run scripts/introduce_vulnerability.sh
    - Wait for Inspector scan (or trigger manual scan)
    - Verify vulnerability detected by Inspector
    - Verify finding appears in Security Hub
    - Run scripts/remediate_vulnerability.sh
    - Verify vulnerability resolved
    - _Requirements: 17.1, 17.2, 17.3, 17.5_

  - [ ]* 21.2 Write infrastructure security validation tests
    - Test that RDS is not publicly accessible
    - Test that S3 bucket blocks public access
    - Test that EC2 instances have no public IPs
    - Test that security groups follow least-privilege
    - Test that IAM role has no admin permissions
    - _Requirements: 4.2, 7.2, 7.7, 9.5, 3.6, 8.6_

- [ ] 22. Final checkpoint - Complete validation
  - Run all unit tests
  - Run all property tests
  - Run all integration tests
  - Run security validation tests
  - Verify all documentation is complete
  - Test vulnerability detection workflow
  - Ensure all lab outcomes are achievable
  - Ask user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- The implementation follows a bottom-up approach: infrastructure → application → testing → documentation
- All secrets are managed by AWS Secrets Manager (no hardcoded credentials)
- The solution supports multiple parallel team deployments through parameterized infrastructure
