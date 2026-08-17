# Terraform GitLab OIDC Bootstrap Module

This module creates AWS IAM resources for GitLab OIDC authentication.

## Features

- Creates OIDC provider for GitLab
- Creates IAM role with proper trust policy
- Supports attaching managed and inline policies
- Configurable session duration
- Environment-aware naming
- Comprehensive tagging
- Security best practices

## Requirements

- Terraform >= 1.6.0
- AWS Provider >= 5.0

## Usage

```hcl
module "gitlab_oidc" {
  source = "./modules/bootstrap-gitlab-oidc"

  project_id   = "12345678"
  environment  = "prod"
  role_name    = "deploy-role"
  policy_arns  = ["arn:aws:iam::aws:policy/AdministratorAccess"]
}
```

Security Considerations
Least Privilege: Attach only necessary policies

Session Duration: Keep max_session_duration reasonable

Conditions: Add additional conditions to trust policy if needed

Tags: Use tags for cost tracking and resource management

Outputs
role_arn: ARN of the IAM role

role_name: Name of the IAM role

oidc_provider_arn: ARN of the OIDC provider

gitlab_oidc_config: Configuration object for GitLab CI

```text
This module follows Terraform best practices including:

1. **Modular Design**: Separated concerns into logical files
2. **Input Validation**: Validates variables with `validation` blocks
3. **Resource Tagging**: All resources are tagged with proper metadata
4. **Lifecycle Management**: Uses `lifecycle` rules to prevent accidental deletion
5. **Sensitive Outputs**: Marks sensitive data appropriately
6. **Documentation**: Includes comprehensive README and inline comments
7. **Flexibility**: Supports both managed and inline policies
8. **Security**: Implements least privilege and proper trust policies
9. **Error Handling**: Uses `depends_on` to ensure proper resource ordering
10. **Version Pinning**: Specifies provider and Terraform versions
```

To use this module, place it in your Terraform configuration and run `terraform init` and `terraform apply` before other modules that might depend on the OIDC role.