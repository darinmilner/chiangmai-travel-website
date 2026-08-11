# Villa Shared Lambda Layer

Shared Python Lambda layer containing common utilities, configuration, and AWS service clients used across all Villa application Lambda functions.

## Overview

This layer provides reusable code for all Villa Lambdas including:
- Shared configuration management
- Structured JSON logging
- AWS service clients (S3, SES, etc.)
- Common utilities and helpers
- Error handling and validation

## Structure

deployment/terraform/lambda-layer/
├── package.py # Packaging script
├── shared-layer/
│ ├── python/ # Layer source code
│ │ └── villa_shared/
│ │ ├── init.py
│ │ ├── config.py # Configuration management
│ │ ├── logging.py # Structured logging
│ │ ├── clients.py # AWS service clients
│ │ └── utils.py # Common utilities
│ └── requirements.txt # Python dependencies
└── dist/ # Packaged layer ZIP files
└── villa-shared-layer-YYYYMMDD.zip


## Prerequisites

- Python 3.13 or 3.14
- pip
- AWS CLI (for deployment)

## Local Development

### Install Dependencies

```bash
cd deployment/terraform/lambda-layer
pip install -r shared-layer/requirements.txt

pytest shared-layer/tests/

python package.py --clean
```

This creates a ZIP file in the dist/ directory with the format villa-shared-layer-YYYYMMDD.zip.

Package Options
Option	Description
--output-dir DIR	Output directory (default: dist)
--clean	Clean output directory before packaging
Examples:

# Basic packaging
python package.py

# Custom output directory
python package.py --output-dir ../build

# Clean and package
python package.py --clean

Deployment
Manual Deployment with AWS CLI

aws lambda publish-layer-version \
    --layer-name villa-shared-layer \
    --description "Shared utilities for Villa Lambdas" \
    --zip-file fileb://dist/villa-shared-layer-20260101.zip \
    --compatible-runtimes python3.11 python3.12 \
    --license-info "MIT"

Terraform Deployment
The layer is deployed using Terraform. Reference it in your Lambda functions:
# In your Terraform configuration
data "aws_lambda_layer_version" "shared" {
  layer_name = "villa-shared-layer"
  version    = 1  # Use latest or specific version
}

resource "aws_lambda_function" "example" {
  # ... other configuration ...

  layers = [
    data.aws_lambda_layer_version.shared.arn
  ]
}

Update Terraform Version
When you publish a new layer version, update your Terraform configuration:
```hcl
data "aws_lambda_layer_version" "shared" {
  layer_name = "villa-shared-layer"
  version    = 2  # Increment to the new version
}
```

Using the Layer in Lambda Functions
Python Import Example
```python
import json
from villa_shared.config import get_config
from villa_shared.logging import get_logger
from villa_shared.clients import get_s3_client, get_ses_client

logger = get_logger()
config = get_config()

def lambda_handler(event, context):
    logger.info("Processing event", extra={"event": event})

    # Use shared clients
    s3 = get_s3_client()
    ses = get_ses_client()

    # Your business logic here

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Success"})
    }
```

Adding Dependencies
Add new dependencies to shared-layer/requirements.txt

Run python package.py --clean to rebuild the layer

Test locally before deploying

Versioning
Layer versions are automatically timestamped when packaged:

Format: villa-shared-layer-YYYYMMDD.zip

Example: villa-shared-layer-20260101.zip

Each deployment creates a new layer version in AWS. Update the version number in your Terraform configuration after deployment.

CI/CD Integration
For automated builds, you can run the packaging script in your CI/CD pipeline:

```yaml
# Example GitHub Actions step
- name: Package Lambda Layer
  run: |
    cd deployment/terraform/lambda-layer
    python package.py --clean

- name: Upload Layer Artifact
  uses: actions/upload-artifact@v3
  with:
    name: lambda-layer
    path: deployment/terraform/lambda-layer/dist/
```

Troubleshooting
Layer Size Exceeds Limit
Lambda layers have a 250 MB (unzipped) limit. Check the size after packaging:
GitLab CI
For automated builds with GitLab CI:

```yaml
# .gitlab-ci.yml
image: python:3.14

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  LAYER_PATH: "deployment/terraform/lambda-layer"

cache:
  paths:
    - .cache/pip

stages:
  - package
  - deploy

package-layer:
  stage: package
  script:
    - cd $LAYER_PATH
    - pip install -r shared-layer/requirements.txt
    - python package.py --clean
  artifacts:
    paths:
      - $LAYER_PATH/dist/*.zip
    expire_in: 1 week
  only:
    changes:
      - deployment/terraform/lambda-layer/**
    - main
    - develop

deploy-layer:
  stage: deploy
  image: amazon/aws-cli:latest
  dependencies:
    - package-layer
  script:
    - LAYER_ZIP=$(ls $LAYER_PATH/dist/*.zip)
    - aws lambda publish-layer-version
        --layer-name villa-shared-layer
        --description "Shared utilities for Villa Lambdas"
        --zip-file fileb://$LAYER_ZIP
        --compatible-runtimes python3.11 python3.12
        --license-info "MIT"
  only:
    - main
  when: manual  # Optional: require manual approval
```

GitLab CI with Terraform Integration
For a complete pipeline including Terraform deployment:

```yaml
# .gitlab-ci.yml
image: python:3.14

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  LAYER_PATH: "deployment/terraform/lambda-layer"
  TF_ROOT: "deployment/terraform"
  TF_VERSION: "1.15.8"

cache:
  paths:
    - .cache/pip

stages:
  - package
  - terraform-plan
  - terraform-apply

package-layer:
  stage: package
  script:
    - cd $LAYER_PATH
    - pip install -r shared-layer/requirements.txt
    - python package.py --clean
  artifacts:
    paths:
      - $LAYER_PATH/dist/*.zip
    expire_in: 1 week
  only:
    changes:
      - deployment/terraform/lambda-layer/**
      - deployment/terraform/**/*.tf
    - main
    - develop

terraform-plan:
  stage: terraform-plan
  image: hashicorp/terraform:$TF_VERSION
  dependencies:
    - package-layer
  before_script:
    - cd $TF_ROOT
    - terraform init
  script:
    - terraform plan -out=plan.tfplan
  artifacts:
    paths:
      - $TF_ROOT/plan.tfplan
    expire_in: 1 week
  only:
    - main
    - develop

terraform-apply:
  stage: terraform-apply
  image: hashicorp/terraform:$TF_VERSION
  dependencies:
    - terraform-plan
  before_script:
    - cd $TF_ROOT
    - terraform init
  script:
    - terraform apply plan.tfplan
  only:
    - main
  when: manual
```

GitLab CI Variables Setup
Configure these variables in your GitLab project:

Variable	Description
AWS_ACCESS_KEY_ID	AWS access key for deployment
AWS_SECRET_ACCESS_KEY	AWS secret access key
AWS_REGION	AWS region (e.g., us-east-1)
For GitLab CI, ensure you have:

AWS credentials configured as CI/CD variables

Appropriate IAM permissions for Lambda layer publishing

Terraform backend configured (S3 + DynamoDB recommended)

Troubleshooting
Layer Size Exceeds Limit
Lambda layers have a 250 MB (unzipped) limit. Check the size after packaging:


```bash
ls -lh dist/*.zip
If too large:
```

Remove unnecessary dependencies

Use --only-binary flag in pip (included in packaging script)

Consider splitting into multiple layers

Dependencies Not Found
Ensure all dependencies are in requirements.txt and the packaging script is run after any changes.

Permission Issues
The packaging script copies files from shared-layer/. Ensure you have read permissions.

Contributing
Add new utilities to shared-layer/python/villa_shared/

Update tests in shared-layer/tests/

Update this README if adding major features

Test locally with python package.py --clean

Submit a pull request

License
MIT