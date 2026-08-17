# Terraform GitLab OIDC Bootstrap Module

This module bootstraps AWS IAM authentication for GitLab CI/CD using
OpenID Connect (OIDC).

It is intended to be run **locally once** using existing AWS credentials.
After the OIDC provider and GitLab deployment role have been created,
GitLab CI/CD can authenticate to AWS without storing long-lived AWS access
keys in GitLab.

The resulting IAM role can then be used by GitLab CI/CD to run Terraform
and deploy AWS infrastructure.

## Architecture

The bootstrap process is:

```text
Developer workstation
        |
        | Existing AWS credentials
        v
Terraform Bootstrap Module
        |
        +------------------------------+
        |                              |
        v                              v
AWS IAM OIDC Provider          GitLab Deployment IAM Role
        |                              |
        +--------------+---------------+
                       |
                       v
                 GitLab CI/CD
                       |
                       | OIDC token
                       v
              AWS STS AssumeRoleWithWebIdentity
                       |
                       v
              Terraform Deployment
                       |
        +--------------+--------------+
        |              |              |
      Lambda          ECR            S3
        |                             |
    API Gateway                   CloudFront
        |
       VPC
        |
       KMS
        |
 Secrets Manager
 ```

# Purpose

This module is a bootstrap module.

It should normally be applied manually from a trusted workstation before
the GitLab CI/CD pipeline is configured to deploy AWS infrastructure.

The module creates:

GitLab's AWS IAM OIDC provider
An IAM deployment role trusted by GitLab OIDC
The permissions required by Terraform to manage the application's
AWS infrastructure

Once the bootstrap is complete, GitLab CI/CD assumes the deployment role
using its OIDC token.

No long-lived AWS access key is required in GitLab CI/CD.

Features
Creates the GitLab OIDC provider
Creates an IAM deployment role
Restricts the trust policy to the specified GitLab project
Uses GitLab project ID as an OIDC trust condition
Supports configurable environment naming
Configurable maximum session duration
Creates permissions for Terraform AWS deployments
Supports Lambda and Lambda Layers
Supports ECR
Supports S3
Supports CloudFront
Supports API Gateway
Supports VPC and EC2 networking resources
Supports KMS
Supports Secrets Manager
Supports IAM resources required by Terraform
Applies consistent resource tags
Prevents accidental OIDC provider deletion
Uses Terraform validation for module inputs
Important: Run This Module Locally First

The GitLab CI/CD pipeline cannot use this OIDC role until the AWS IAM
OIDC provider already exists.

Therefore, the bootstrap module must initially be run using existing AWS
credentials.

For example:
cd terraform/bootstrap-gitlab-oidc

terraform init
terraform plan
terraform apply

After the module has been successfully applied, the resulting IAM role ARN
can be configured in the GitLab project.

The normal deployment flow then becomes:
```text
1. Run bootstrap module locally
             |
             v
2. OIDC provider created
             |
             v
3. IAM deployment role created
             |
             v
4. Configure role ARN in GitLab
             |
             v
5. GitLab pipeline starts
             |
             v
6. GitLab issues OIDC token
             |
             v
7. AWS STS validates token
             |
             v
8. GitLab assumes deployment role
             |
             v
9. Terraform deploys infrastructure
```

Requirements
Terraform >= 1.6.0
AWS Provider >= 5.0
AWS credentials with sufficient permissions to create:
IAM OIDC provider
IAM roles
IAM policies
IAM policy attachments
A GitLab project
GitLab project ID

The bootstrap must be run from an environment that already has AWS
credentials.

For example:

aws sts get-caller-identity

should successfully return the AWS account and identity being used.

# Usage

The module is intended to be called from a small standalone Terraform
configuration.

For example:
```hcl
module "gitlab_oidc" {
  source = "./modules/bootstrap-gitlab-oidc"

  project_id  = "12323432"
  environment = "dev"
}
```

The module uses the AWS account ID from the AWS caller identity data source,
so an account_id variable is not required.

The role name is generated automatically using the application name and
environment.

For example:

chiangmaivilla-gitlab-oidc-deploy-dev
Bootstrap Directory Example

A recommended structure is:
```text
terraform/
│
├── bootstrap/
│   └── gitlab-oidc/
│       ├── main.tf
│       ├── variables.tf
│       ├── locals.tf
│       ├── outputs.tf
│       ├── providers.tf
│       └── versions.tf
│
├── modules/
│   └── bootstrap-gitlab-oidc/
│       ├── main.tf
│       ├── variables.tf
│       ├── locals.tf
│       ├── outputs.tf
│       └── README.md
│
└── infrastructure/
    ├── lambda/
    ├── ecr/
    ├── s3/
    ├── cloudfront/
    ├── api-gateway/
    ├── vpc/
    ├── kms/
    └── secrets-manager/
```
The bootstrap/gitlab-oidc configuration calls the reusable module.

GitLab Project Restriction

The IAM trust policy restricts authentication to the configured GitLab
project.

The module uses the GitLab OIDC project_id claim:
```hcl
Condition = {
  StringEquals = {
    "${local.oidc_provider_url}:project_id" = var.project_id
  }
}
```

This prevents another GitLab project from assuming the deployment role.

Additional restrictions can be added if required.

For example, the trust policy could additionally restrict the role to a
specific branch or tag:

```hcl
StringLike = {
  "${local.oidc_provider_url}:ref_type" = "branch"
  "${local.oidc_provider_url}:ref"      = "main"
}
```

Branch restrictions should be considered carefully because they affect
merge request pipelines and deployment workflows.

AWS Permissions

The deployment role is intended to be used by Terraform.

The current policy allows Terraform to manage resources required by this
project, including:

Lambda
Create, update and delete Lambda functions
Publish Lambda versions
Create and manage aliases
Publish Lambda layers
Manage event source mappings
Manage Lambda permissions and tags
ECR
Authenticate to ECR
Create and manage repositories
Push and pull images
Manage repository images and tags
S3
Create and manage buckets
Manage bucket policies
Manage encryption
Manage versioning
Manage objects
CloudFront
Create and manage distributions
Create and manage Origin Access Controls
Manage CloudFront tags
API Gateway
Create, update and delete API Gateway resources
VPC / EC2 Networking
VPCs
Subnets
Route tables
Routes
Internet gateways
NAT gateways
Security groups
Elastic IP addresses
Network interfaces
Resource tagging
KMS
Create and manage KMS keys
Create and manage aliases
Manage key policies
Schedule and cancel key deletion
Manage tags
Secrets Manager
Create and manage secrets
Read and update secret values
Manage secret versions
Manage tags
IAM

Terraform requires IAM permissions because the infrastructure itself may
create execution roles for Lambda and other AWS services.

The deployment role therefore includes permissions such as:

iam:CreateRole
iam:DeleteRole
iam:GetRole
iam:UpdateRole
iam:AttachRolePolicy
iam:DetachRolePolicy
iam:PutRolePolicy
iam:DeleteRolePolicy
iam:CreatePolicy
iam:DeletePolicy
iam:CreatePolicyVersion
iam:DeletePolicyVersion
iam:PassRole

iam:PassRole should be reviewed carefully because it allows the Terraform
deployment role to pass IAM roles to AWS services.

For a production environment, these permissions should ideally be
restricted to specific resource ARNs where practical.

GitLab CI/CD

After the bootstrap has been completed, the GitLab pipeline can use AWS
OIDC authentication.

The GitLab project should be configured with the IAM role ARN generated by
this module.

The pipeline can then exchange the GitLab OIDC token for temporary AWS
credentials.

Conceptually:
```text
GitLab Job
    |
    | CI_JOB_JWT / ID token
    v
GitLab OIDC
    |
    v
AWS STS
    |
    | AssumeRoleWithWebIdentity
    v
GitLab Terraform IAM Role
    |
    v
Terraform
```
The pipeline should not contain:

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

for this authentication flow.

Instead, GitLab provides a short-lived OIDC identity token.

Deployment Workflow

Once bootstrap is complete, the repository can use GitLab CI/CD for
Terraform deployments.

A typical workflow is:
```text
Developer
   |
   v
GitLab Merge Request
   |
   v
Terraform fmt / validate
   |
   v
Terraform plan
   |
   v
Merge to main
   |
   v
Terraform apply
   |
   v
AWS
```

The GitLab pipeline can then deploy:

Lambda
Lambda Layers
ECR
S3
CloudFront
API Gateway
VPC
KMS
Secrets Manager
IAM
Outputs

The module provides information needed to configure GitLab CI/CD.

role_arn

ARN of the IAM deployment role.

Example:

arn:aws:iam::123456789012:role/chiangmaivilla-gitlab-oidc-deploy-dev
role_name

Name of the IAM deployment role.

oidc_provider_arn

ARN of the GitLab IAM OIDC provider.

gitlab_oidc_config

Configuration information required by the GitLab CI/CD deployment.

# Security Considerations
Least Privilege

The deployment role should only have the AWS permissions required by the
Terraform configuration.

The current policy is intentionally broad because Terraform is responsible
for deploying multiple AWS services.

As the infrastructure becomes stable, permissions should be reduced and
resource ARNs should be used where practical.

GitLab Project Restriction

The trust policy restricts role assumption to the configured GitLab project:

"${local.oidc_provider_url}:project_id" = var.project_id

This is an important security control and should be retained.

Branch Restrictions

Additional OIDC conditions can restrict deployments to specific branches
or tags.

For example:
```hcl
"${local.oidc_provider_url}:ref" = "main"
```

This can prevent feature branches from assuming a production deployment
role.

IAM PassRole

The Terraform deployment role requires iam:PassRole when Terraform
creates AWS service roles.

This permission should be restricted to specific role ARNs in a production
environment whenever possible.

Session Duration

Keep the maximum session duration appropriate for the expected Terraform
deployment time.

The default is:

3600 seconds

The maximum supported by the module is:

43200 seconds
OIDC Provider Lifecycle

The OIDC provider uses:

lifecycle {
  prevent_destroy = true
}

This helps prevent accidentally breaking GitLab CI/CD authentication.

Because the OIDC provider is a bootstrap resource, it should not normally
be destroyed as part of application infrastructure changes.

Terraform Best Practices

This module follows Terraform best practices including:

Bootstrap Separation
The OIDC infrastructure is separated from the application's Terraform
deployment.
Modular Design
The GitLab OIDC resources are contained in a reusable module.
AWS Account Discovery
The AWS account ID is obtained using
aws_caller_identity instead of requiring an account ID variable.
Input Validation
Variables use Terraform validation blocks where appropriate.
Resource Tagging
AWS resources are tagged consistently.
Lifecycle Management
The OIDC provider uses prevent_destroy to reduce the risk of
accidentally breaking CI/CD authentication.
Project-Level Trust
The IAM trust policy is restricted using the GitLab project ID.
Temporary AWS Credentials
GitLab CI/CD uses OIDC instead of long-lived AWS access keys.
Infrastructure Separation
Bootstrap resources are created separately from application
infrastructure.
Reusable Deployment Identity
The resulting IAM role can be used by GitLab Terraform jobs to deploy
the application's AWS infrastructure.
Important: Do Not Run Bootstrap on Every Pipeline

This module is not intended to run as part of every GitLab pipeline.

Run it once when establishing GitLab-to-AWS federation.

After that, the normal GitLab pipeline should use the IAM deployment role
created by this module.

Bootstrap
─────────
Run locally
     |
     +── OIDC Provider
     |
     +── GitLab Deployment Role
     |
     └── Configure GitLab
              |
              v
Normal CI/CD
────────────
GitLab OIDC
     |
     v
Assume Deployment Role
     |
     v
Terraform Plan / Apply
     |
     v
AWS Infrastructure
Initial Setup

From the bootstrap directory:

terraform init

Review the planned resources:

terraform plan

Apply the bootstrap configuration:

terraform apply

Verify the resulting role:

terraform output role_arn

Verify the AWS identity:

aws sts get-caller-identity

The resulting IAM role ARN should then be configured for the GitLab
project's CI/CD OIDC authentication.

After Bootstrap

Once the bootstrap is complete, the GitLab repository can use the resulting
role to deploy the application's Terraform infrastructure.

The bootstrap module should generally remain separate from the application's
Terraform state and deployment pipeline.

This separation ensures that the mechanism used to authenticate GitLab to
AWS does not depend on the infrastructure that GitLab is responsible for
deploying.