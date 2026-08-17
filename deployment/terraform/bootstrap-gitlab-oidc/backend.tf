terraform {
  backend "s3" {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta"
    key    = "gitlab-oidc/terraform.tfstate"
    region = "ap-southeast-7"
  }

  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-7"
}
