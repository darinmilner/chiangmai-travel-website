terraform {
  backend "s3" {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta"
    key    = "statefiles/contact-lambda/terraform.tfstate"
    region = "ap-southeast-7"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}


# Configure multiple AWS providers for different regions
provider "aws" {
  alias  = "bangkok"
  region = var.bangkok_region
}

provider "aws" {
  alias  = "singapore"
  region = var.singapore_region
}

# Default provider (used for resources that don't specify a region)
provider "aws" {
  region = var.bangkok_region
}
