terraform {
  backend "s3" {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta"
    key    = "statefiles/route53/terraform.tfstate"
    region = "ap-southeast-7"
  }

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 6.0"
      configuration_aliases = [aws.us-east1]
    }
  }
}

provider "aws" {
  region = "ap-southeast-7"
}

# Provider required for CloudFront ACM Certificate
provider "aws" {
  alias  = "us-east1"
  region = "us-east-1"
}