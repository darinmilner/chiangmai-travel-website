# backend.tf
terraform {
  backend "s3" {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta"
    key    = "statefiles/lambda-layer/terraform.tfstate"
    region = "ap-southeast-7"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.region
}
