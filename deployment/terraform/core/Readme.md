Creates an S3 Bucket to store TF state files and .env files Creates IAM Roles for using Github Actions and ECS Creates An OIDC token provider for Github Actions to connect to AWS Important - Run this module before creating any other resources

use_kms bool is set to false by default. Change to true before production to add KMS encryption to the bucket for extra security

Environment	use_kms	Encryption	Role Permissions
Beta / Testing	false	SSE-S3	S3 only
Pre-prod / Prod	true	SSE-KMS	S3 + KMS access