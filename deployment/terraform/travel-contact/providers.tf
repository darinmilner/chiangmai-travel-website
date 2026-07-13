terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
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
